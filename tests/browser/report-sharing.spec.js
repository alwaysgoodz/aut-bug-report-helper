const { test, expect } = require('@playwright/test');
const fs = require('node:fs/promises');

test('Saved report copies current content, handles clipboard rejection and still downloads', async ({ page, context }) => {
  await context.grantPermissions(['clipboard-read', 'clipboard-write']);
  await page.goto('/reports/new');
  const title = 'Portable export 演示 sample';
  await page.locator('#title').fill(title);
  await page.locator('#severity').selectOption('low');
  await page.getByRole('button', { name: 'Create report', exact: true }).click();
  await page.locator('#status').selectOption('In progress');
  await page.getByRole('button', { name: 'Update status', exact: true }).click();
  await page.getByRole('button', { name: 'Copy report', exact: true }).click();
  await expect(page.locator('#copy-feedback')).toHaveText('Report copied. Ready to share.');
  const copied = await page.evaluate(() => navigator.clipboard.readText());
  expect(copied).toContain(title);
  expect(copied).toContain('Status: In progress');
  await page.evaluate(() => Object.defineProperty(navigator.clipboard, 'writeText', {
    value: () => Promise.reject(new DOMException('Test permission rejection', 'NotAllowedError')),
  }));
  await page.getByRole('button', { name: 'Copy report', exact: true }).click();
  await expect(page.locator('#copy-feedback')).toHaveText('Copy was unavailable. Use Download report to save a file.');
  await expect(page.getByRole('button', { name: 'Copy report', exact: true })).toBeEnabled();
  const pendingDownload = page.waitForEvent('download');
  await page.getByRole('link', { name: 'Download report', exact: true }).click();
  const download = await pendingDownload;
  expect(download.suggestedFilename()).toMatch(/^bug-report-[0-9a-f-]+\.md$/);
  // Windows clipboard storage normalises LF to CRLF; compare content, not its
  // platform line-ending representation, while retaining every other character.
  expect((await fs.readFile(await download.path(), 'utf8')).replace(/\r\n/g, '\n')).toBe(copied.replace(/\r\n/g, '\n'));
  await page.setViewportSize({ width: 320, height: 700 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});

test.describe('Native report download', () => {
  test.use({ javaScriptEnabled: false });
  test('download works without JavaScript and copying is not falsely offered', async ({ page }) => {
    await page.goto('/reports/new');
    await page.locator('#title').fill('Native downloadable report');
    await page.locator('#severity').selectOption('low');
    await page.getByRole('button', { name: 'Create report', exact: true }).click();
    await expect(page.getByRole('button', { name: 'Copy report', exact: true })).toHaveCount(0);
    const pendingDownload = page.waitForEvent('download');
    await page.getByRole('link', { name: 'Download report', exact: true }).click();
    const download = await pendingDownload;
    expect(await fs.readFile(await download.path(), 'utf8')).toContain('Native downloadable report');
  });
});
