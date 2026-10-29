const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '../..');
// Enumerate published source pages, not dependency/report HTML.
function pages(dir, prefix = '') {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap(entry => {
    if (['.git', 'node_modules', 'tmp', 'test-results', 'playwright-report'].includes(entry.name)) return [];
    const rel = prefix + entry.name;
    if (entry.isDirectory()) return pages(path.join(dir, entry.name), rel + '/');
    return entry.name.endsWith('.html') ? [rel] : [];
  });
}
const sourcePages = pages(root);
const urlFor = file => '/' + file.replace(/index\.html$/, '').replace(/\.html$/, '');
for (const size of [{ width: 1280, height: 900 }, { width: 390, height: 844 }]) {
  test.describe(size.width + 'px viewport', () => {
    test.use({ viewport: size });
    for (const file of sourcePages) {
      test(file, async ({ page }, testInfo) => {
        // Isolated localhost test: no account/profile or external traffic.
        await page.route('**/*', route => {
          const url = new URL(route.request().url());
          return url.origin === 'http://127.0.0.1:8765'
            ? route.continue() : route.abort();
        });
        const failures = [];
        page.on('pageerror', error => failures.push(error.message));
        page.on('response', response => {
          if (response.url().startsWith('http://127.0.0.1:8765') && response.status() >= 400) {
            failures.push(response.status() + ' ' + response.url());
          }
        });
        const response = await page.goto(urlFor(file));
        expect(response.status()).toBe(200);
        await page.evaluate(() => document.fonts.ready);
        await expect(page.locator('h1')).toHaveCount(1);
        await expect(page.locator('h1')).toBeVisible();
        expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
        expect(await page.locator('img').evaluateAll(images => images.filter(i => i.loading !== 'lazy').every(i => i.complete && i.naturalWidth > 0))).toBe(true);
        if (file.includes('insights/') || ['insights.html', 'en/insights.html'].includes(file)) {
          await page.screenshot({ path: testInfo.outputPath('top.png') });
          await page.screenshot({ path: testInfo.outputPath('page.png'), fullPage: true });
        }
        if (file.includes('insights/')) {
          const alternate = page.locator('.lang-switcher a:not([aria-current])');
          const target = await alternate.getAttribute('href');
          await alternate.click();
          await expect(page).toHaveURL('http://127.0.0.1:8765' + target);
          if (size.width === 390) {
            const toggle = page.locator('.nav-toggle');
            await toggle.click();
            await expect(toggle).toHaveAttribute('aria-expanded', 'true');
            await page.keyboard.press('Escape');
            await expect(toggle).toHaveAttribute('aria-expanded', 'false');
            await expect(toggle).toBeFocused();
          }
        }
        expect(failures).toEqual([]);
      });
    }
  });
}
