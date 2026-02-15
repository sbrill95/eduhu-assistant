import { test, expect } from '@playwright/test';

test('production verification', async ({ page }) => {
    // Go to production URL
    await page.goto('https://eduhu-assistant.pages.dev/');

    // Check title or content to verify it loads
    const title = await page.title();
    console.log(`Page title: ${title}`);

    // It should probably show the login screen or similar
    // Let's take a screenshot for visual verification (saved locally)
    await page.screenshot({ path: 'e2e/production_screenshot.png' });

    // Verify some basics
    // If "Vite + React" is default, or "eduhu-assistant"
    // Just checking if body is present means something loaded
    await expect(page.locator('body')).toBeVisible();
});
