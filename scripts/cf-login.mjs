import puppeteer from 'puppeteer-core';

const browser = await puppeteer.launch({
  executablePath: '/snap/bin/chromium',
  headless: 'new',
  args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu']
});

const page = await browser.newPage();
console.log('Going to Cloudflare login...');
await page.goto('https://dash.cloudflare.com/login', { waitUntil: 'networkidle2' });

// Check if it's GitHub OAuth login or email/password
const content = await page.content();
console.log('Page title:', await page.title());

// Try to find login with GitHub button or email field
const emailField = await page.$('input[type="email"]');
if (emailField) {
  console.log('Found email field, typing...');
  await emailField.type('s.brill@eduhu.de');
  
  // Click "Log in" or "Sign in" button
  const buttons = await page.$$('button');
  for (const btn of buttons) {
    const text = await btn.evaluate(el => el.textContent.trim());
    console.log('Button found:', text);
  }
  
  // Find submit button
  const submitBtn = await page.$('button[type="submit"]');
  if (submitBtn) {
    await submitBtn.click();
    console.log('Clicked submit');
    await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 10000 }).catch(() => {});
    
    // Check for password field
    const pwField = await page.$('input[type="password"]');
    if (pwField) {
      console.log('Found password field, typing...');
      await pwField.type('asfqegasgagoninioasg!1');
      const submitBtn2 = await page.$('button[type="submit"]');
      if (submitBtn2) {
        await submitBtn2.click();
        console.log('Clicked submit (password)');
        await page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 15000 }).catch(() => {});
      }
    }
  }
}

// Look for "Sign in with GitHub" link
const githubLink = await page.$('a[href*="github"]');
if (githubLink) {
  console.log('Found GitHub sign-in link');
}

console.log('Current URL:', page.url());
console.log('Page title:', await page.title());

// Take screenshot for debugging
await page.screenshot({ path: '/tmp/cf-login.png' });
console.log('Screenshot saved to /tmp/cf-login.png');

await browser.close();
