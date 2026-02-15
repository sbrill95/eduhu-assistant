"""
E2E Tests — Ebene 3: Playwright - Tests gegen die laufende App.

Diese Tests brauchen:
- Einen laufenden Backend - Server
    - Einen laufenden Frontend - Dev - Server
        - Echte DB - Verbindung(oder Staging)

Konfiguration über Umgebungsvariablen:
BASE_URL = http://localhost:5173       (Frontend)
BACKEND_URL = http://localhost:8000       (Backend API)
TEACHER_PASSWORD = demo123(Login - Passwort)
"""

import { test, expect, type Page, type Download } from '@playwright/test';

// ── Config ──
const BASE_URL = process.env.BASE_URL || 'http://localhost:5173';
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';
const PASSWORD = process.env.TEACHER_PASSWORD || 'demo123';

// ── Helpers ──

/** Login and return the teacher_id */
async function login(page: Page): Promise<string> {
    await page.goto(BASE_URL);

    // Wait for login form
    const passwordInput = page.locator('input[type="password"]');
    await expect(passwordInput).toBeVisible({ timeout: 10000 });

    await passwordInput.fill(PASSWORD);
    await page.keyboard.press('Enter');

    // Wait for redirect after login (dashboard or chat)
    await page.waitForURL(/\/(chat|dashboard|profile)/, { timeout: 15000 });

    // Get teacher ID from localStorage or cookie
    const teacherId = await page.evaluate(() => localStorage.getItem('teacher_id'));
    expect(teacherId).toBeTruthy();

    return teacherId!;
}


// ═══════════════════════════════════════
// E2E-1: Login Flow
// ═══════════════════════════════════════

test.describe('Login', () => {
    test('should login with valid password', async ({ page }) => {
        const teacherId = await login(page);
        expect(teacherId).toBeTruthy();
    });

    test('should reject invalid password', async ({ page }) => {
        await page.goto(BASE_URL);
        const input = page.locator('input[type="password"]');
        await expect(input).toBeVisible({ timeout: 10000 });
        await input.fill('wrongpassword');
        await page.keyboard.press('Enter');

        // Should show error — NOT redirect
        await expect(page.locator('text=/falsch|fehler|ungültig/i')).toBeVisible({ timeout: 5000 });
    });
});


// ═══════════════════════════════════════
// E2E-2: Profile Flow
// ═══════════════════════════════════════

test.describe('Profile', () => {
    test('should display and update profile', async ({ page }) => {
        await login(page);

        // Navigate to profile
        await page.click('a[href*="/profile"], [data-testid="nav-profile"]');
        await page.waitForURL(/\/profile/, { timeout: 10000 });

        // Check that profile form exists
        await expect(page.locator('select, input[name="bundesland"], [data-testid="bundesland"]')).toBeVisible({ timeout: 5000 });

        // Select Bundesland if dropdown
        const dropdown = page.locator('select[name="bundesland"], [data-testid="bundesland-select"]');
        if (await dropdown.isVisible()) {
            await dropdown.selectOption({ label: 'Sachsen' });
        }

        // Save
        const saveBtn = page.locator('button:has-text("Speichern"), button[type="submit"]');
        if (await saveBtn.isVisible()) {
            await saveBtn.click();
            // Should show success feedback
            await expect(page.locator('text=/gespeichert|erfolg|✓/i')).toBeVisible({ timeout: 5000 });
        }
    });
});


// ═══════════════════════════════════════
// E2E-3: Chat Flow
// ═══════════════════════════════════════

test.describe('Chat', () => {
    test('should send message and receive AI response', async ({ page }) => {
        test.setTimeout(120000); // AI responses can be slow

        await login(page);

        // Navigate to chat
        await page.click('a[href*="/chat"], [data-testid="nav-chat"]');
        await page.waitForURL(/\/chat/, { timeout: 10000 });

        // Type message
        const textarea = page.locator('textarea, input[type="text"][placeholder*="Nachricht"]');
        await expect(textarea).toBeVisible({ timeout: 5000 });
        await textarea.fill('Erstelle mir einen kurzen Unterrichtsplan für Biologie Klasse 7 zum Thema Zelle.');

        // Send
        await page.keyboard.press('Enter');

        // Wait for AI response (look for assistant message bubble)
        const responseLocator = page.locator('.prose, [data-role="assistant"], [class*="assistant"]').last();
        await expect(responseLocator).toContainText(/Zelle|Unterricht|Biologie/i, { timeout: 90000 });
    });

    test('should handle agent ask-back on vague input', async ({ page }) => {
        test.setTimeout(120000);

        await login(page);
        await page.click('a[href*="/chat"], [data-testid="nav-chat"]');
        await page.waitForURL(/\/chat/, { timeout: 10000 });

        const textarea = page.locator('textarea, input[type="text"][placeholder*="Nachricht"]');
        await expect(textarea).toBeVisible({ timeout: 5000 });
        await textarea.fill('Erstelle Material.');
        await page.keyboard.press('Enter');

        // Agent should ask back — NOT immediately generate
        const responseLocator = page.locator('.prose, [data-role="assistant"]').last();
        await expect(responseLocator).toContainText(/welch|Thema|Fach|Klasse|genauer/i, { timeout: 90000 });
    });
});


// ═══════════════════════════════════════
// E2E-4: Material Generation & Download
// ═══════════════════════════════════════

test.describe('Material Generation', () => {
    test('should generate exam and provide DOCX download', async ({ page }) => {
        test.setTimeout(180000); // Material generation is slow

        await login(page);

        // Navigate to chat and request material
        await page.click('a[href*="/chat"], [data-testid="nav-chat"]');
        await page.waitForURL(/\/chat/, { timeout: 10000 });

        const textarea = page.locator('textarea, input[type="text"][placeholder*="Nachricht"]');
        await expect(textarea).toBeVisible({ timeout: 5000 });

        // Give explicit instructions so agent doesn't ask back
        await textarea.fill('Erstelle eine Physik-Klausur für Klasse 9 zum Thema Mechanik. 3 Aufgaben, 45 Minuten, AFB I-III gleichmäßig verteilt.');
        await page.keyboard.press('Enter');

        // Wait for response with download link
        const downloadLink = page.locator('a[href*="/api/materials/"][href*="/docx"]');
        await expect(downloadLink).toBeVisible({ timeout: 120000 });

        // Click download and verify file
        const [download] = await Promise.all([
            page.waitForEvent('download', { timeout: 30000 }),
            downloadLink.click(),
        ]);

        expect(download.suggestedFilename()).toMatch(/\.docx$/);
    });
});


// ═══════════════════════════════════════
// E2E-5: Conversation Persistence
// ═══════════════════════════════════════

test.describe('Conversation Persistence', () => {
    test('should show conversations in sidebar', async ({ page }) => {
        test.setTimeout(120000);

        await login(page);
        await page.click('a[href*="/chat"], [data-testid="nav-chat"]');
        await page.waitForURL(/\/chat/, { timeout: 10000 });

        // Send a message to create a conversation
        const textarea = page.locator('textarea, input[type="text"][placeholder*="Nachricht"]');
        await textarea.fill('Sag mir kurz Hallo.');
        await page.keyboard.press('Enter');

        // Wait for response
        await expect(page.locator('.prose, [data-role="assistant"]').last()).toContainText(/.+/, { timeout: 60000 });

        // Refresh page
        await page.reload();
        await page.waitForLoadState('networkidle');

        // Conversation should still be listed
        const sidebar = page.locator('[class*="sidebar"], [data-testid="conversation-list"], nav');
        // At least one conversation item
        await expect(sidebar.locator('a, button, [class*="conversation"]').first()).toBeVisible({ timeout: 10000 });
    });
});


// ═══════════════════════════════════════
// E2E-6: API Health (Backend Smoke Test)
// ═══════════════════════════════════════

test.describe('Backend Health', () => {
    test('API health endpoint returns ok', async ({ request }) => {
        const response = await request.get(`${BACKEND_URL}/api/health`);
        expect(response.status()).toBe(200);
        const data = await response.json();
        expect(data.status).toBe('ok');
    });
});
