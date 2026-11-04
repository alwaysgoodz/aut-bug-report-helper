const { test, expect } = require('@playwright/test');
test.beforeAll(async ({ browser }) => {
  console.log(`Browser under test: ${browser.version()}`);
});

async function create(page, title, severity = 'high') {
  await page.goto('/reports/new');
  await page.locator('#title').fill(title);
  await page.locator('#description').fill('Synthetic acceptance example for the course project.');
  await page.locator('#steps').fill('1. Open the app\n2. Open settings');
  await page.locator('#expected').fill('Settings controls appear');
  await page.locator('#actual').fill('The panel is blank');
  await page.locator('#environment').fill('Demo build / Chromium');
  await page.locator('#severity').selectOption(severity);
  await page.getByRole('button', { name: 'Create report', exact: true }).click();
  await expect(page.getByRole('heading', { name: title, exact: true })).toBeVisible();
}

test('C1: invalid submission retains input, inserts nothing and focuses linked summary', async ({ page }) => {
  await page.goto('/');
  const before = await page.locator('.stats .stat strong').first().textContent();
  await page.goto('/reports/new');
  await page.locator('#title').fill('   ');
  await page.locator('#steps').fill('Keep these reproduction steps');
  await page.getByRole('button', { name: 'Create report', exact: true }).click();
  await expect(page.locator('#form-errors')).toBeVisible();
  await expect(page.locator('#form-errors')).toBeFocused();
  await expect(page.locator('#steps')).toHaveValue('Keep these reproduction steps');
  await expect(page.locator('#form-errors a[href="#title"]')).toBeVisible();
  await expect(page.locator('#title')).toHaveAttribute('aria-invalid', 'true');
  await page.goto('/');
  await expect(page.locator('.stats .stat strong').first()).toHaveText(before);
});

test('C2: create and reload a persisted report without duplicating it', async ({ page }) => {
  const title = 'C2 settings panel is blank';
  await create(page, title);
  await page.reload();
  await expect(page.getByRole('heading', { name: title, exact: true })).toBeVisible();
  await expect(page.getByText('1. Open the app\n2. Open settings', { exact: true })).toBeVisible();
  await page.goto('/');
  await expect(page.getByRole('link', { name: title, exact: true })).toHaveCount(1);
});

test('C3: status cycle and reopening persist through navigation', async ({ page }) => {
  await create(page, 'C3 status lifecycle');
  for (const status of ['In progress', 'Resolved', 'Open']) {
    await page.locator('#status').selectOption(status);
    await page.getByRole('button', { name: 'Update status', exact: true }).click();
    await expect(page.locator('#status')).toHaveValue(status);
    await page.reload();
    await expect(page.locator('#status')).toHaveValue(status);
  }
});

test('BR-04: live guidance and saved score agree on zero, six and seven fields', async ({ page }) => {
  await page.goto('/reports/new');
  await expect(page.locator('#completeness-score')).toHaveText('0%');
  await page.locator('#title').fill('   ');
  await expect(page.locator('#completeness-score')).toHaveText('0%');
  for (const field of ['title', 'description', 'steps', 'expected', 'actual', 'environment']) {
    await page.locator('#' + field).fill(field === 'title' ? 'BR04 guidance boundary' : 'A useful detail');
  }
  await expect(page.locator('#completeness-score')).toHaveText('86%');
  await expect(page.locator('#missing-fields li:visible')).toHaveCount(1);
  await expect(page.locator('#missing-fields li:visible strong')).toHaveText('Severity');
  await page.locator('#severity').selectOption('medium');
  await expect(page.locator('#completeness-score')).toHaveText('100%');
  await expect(page.locator('#guidance-complete')).toBeVisible();
  await page.getByRole('button', { name: 'Create report', exact: true }).click();
  await expect(page.locator('#completeness-score')).toHaveText('100%');
  await expect(page.getByText('Information presence, not correctness.', { exact: false })).toBeVisible();
});

test('BR-05: AND filters, no matches and clearing leave stored reports intact', async ({ page }) => {
  await create(page, 'BR05 critical resolved', 'critical');
  for (const status of ['In progress', 'Resolved']) {
    await page.locator('#status').selectOption(status);
    await page.getByRole('button', { name: 'Update status', exact: true }).click();
  }
  await create(page, 'BR05 low open', 'low');
  await page.goto('/');
  const before = await page.locator('.stats .stat strong').first().textContent();
  await page.locator('#filter-severity').selectOption('critical');
  await page.locator('#filter-status').selectOption('Resolved');
  await page.getByRole('button', { name: 'Apply filters', exact: true }).click();
  await expect(page.getByRole('link', { name: 'BR05 critical resolved', exact: true })).toBeVisible();
  await expect(page.getByRole('link', { name: 'BR05 low open', exact: true })).toHaveCount(0);
  await page.locator('#filter-status').selectOption('In progress');
  await page.getByRole('button', { name: 'Apply filters', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'No reports match these filters', exact: true })).toBeVisible();
  await page.getByRole('link', { name: 'Clear filters', exact: true }).click();
  await expect(page.getByRole('link', { name: 'BR05 low open', exact: true })).toBeVisible();
  await expect(page.locator('.stats .stat strong').first()).toHaveText(before);
});

test('BR-02: the form can be completed and submitted with the keyboard', async ({ page }) => {
  await page.goto('/reports/new');
  await page.locator('#title').focus();
  const fields = ['title', 'description', 'steps', 'expected', 'actual', 'environment'];
  for (const field of fields) {
    await expect(page.locator('#' + field)).toBeFocused();
    await page.keyboard.type(field === 'title' ? 'Keyboard acceptance report' : 'Keyboard-entered context');
    await page.keyboard.press('Tab');
  }
  await expect(page.locator('#severity')).toBeFocused();
  await page.keyboard.press('Home');
  await page.keyboard.press('ArrowDown');
  await page.keyboard.press('ArrowDown');
  await page.keyboard.press('ArrowDown');
  await page.keyboard.press('Tab');
  await expect(page.getByRole('link', { name: 'Cancel', exact: true })).toBeFocused();
  await page.keyboard.press('Tab');
  await expect(page.getByRole('button', { name: 'Create report', exact: true })).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.getByRole('heading', { name: 'Keyboard acceptance report', exact: true })).toBeVisible();
});

test('Responsive layout and escaped HTML remain usable on a narrow screen', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await create(page, '<img src=x onerror=alert(1)>', 'low');
  await expect(page.locator('main img')).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Update status', exact: true })).toBeVisible();
  await page.goto('/reports/new');
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await expect(page.locator('#title')).toBeVisible();
  await expect(page.locator('#completeness-score')).toHaveText('0%');
});

test('Shared Unicode whitespace gives consistent live validation and saved completeness', async ({ page }) => {
  await page.goto('/reports/new');
  await page.locator('#severity').selectOption('high');
  for (const value of ['\u0085', '\ufeff', '\u001c\u00a0\ufeff']) {
    await page.locator('#title').fill(value);
    await expect(page.locator('#completeness-score')).toHaveText('14%');
  }
  await page.getByRole('button', { name: 'Create report', exact: true }).click();
  await expect(page.locator('#form-errors')).toBeFocused();
  await expect(page.locator('#completeness-score')).toHaveText('14%');
  await page.locator('#title').fill('\ufeffUnicode boundary report\u0085');
  await page.getByRole('button', { name: 'Create report', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Unicode boundary report', exact: true })).toBeVisible();
  await expect(page.locator('#completeness-score')).toHaveText('29%');
});

test('Missing-information guidance links move focus to the actual form control', async ({ page }) => {
  await page.goto('/reports/new');
  await page.locator('#missing-fields a[href="#steps"]').click();
  await expect(page.locator('#steps')).toBeFocused();
  await page.keyboard.type('Steps entered from the guidance link');
  await expect(page.locator('#completeness-score')).toHaveText('14%');
  await expect(page.locator('#missing-fields li[data-field="steps"]')).toBeHidden();
});

test('List, detail and grouped form fit phone, tablet and desktop with readable labels', async ({ page }) => {
  await create(page, 'Responsive acceptance sample');
  for (const width of [390, 768, 1440]) {
    await page.setViewportSize({ width, height: 1000 });
    await page.goto('/');
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    const row = page.locator('tbody tr').first();
    await expect(row.locator('[data-label="Status"]')).toBeVisible();
    await expect(row.locator('[data-label="Completeness"]')).toBeVisible();
    expect(await row.locator('.badge').first().evaluate(el => parseFloat(getComputedStyle(el).fontSize))).toBeGreaterThanOrEqual(12);
    await row.locator('.report-title').click();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    await expect(page.locator('#status')).toBeVisible();
    await expect(page.locator('#completeness-score')).toBeVisible();
    await page.goto('/reports/new');
    await expect(page.getByRole('heading', { name: 'The issue', exact: true })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Reproduce it', exact: true })).toBeVisible();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    expect(await page.locator('#title').evaluate(el => parseFloat(getComputedStyle(el).fontSize))).toBeGreaterThanOrEqual(16);
    if (width < 1050) {
      await expect(page.locator('.guidance-details')).not.toHaveAttribute('open', '');
      await page.locator('.guidance-details summary').click();
      await expect(page.locator('#missing-fields li:visible')).toHaveCount(7);
    }
  }
});

test('Pagination retains filters, exposes every inserted report and resets when a filter is removed', async ({ page }) => {
  await page.goto('/reports/new');
  const token = await page.locator('input[name="_csrf"]').inputValue();
  const inserted = [];
  for (let index = 0; index < 30; index++) {
    const response = await page.request.post('/reports', { form: { _csrf: token, title: `Pagination sample ${index}`, severity: 'high' } });
    expect(response.ok()).toBe(true);
    inserted.push(new URL(response.url()).pathname.split('/')[2]);
  }
  await page.goto('/?severity=high&status=Open');
  await expect(page.locator('tbody tr')).toHaveCount(25);
  const first = await page.locator('tbody tr').evaluateAll(rows => rows.map(row => row.dataset.reportId));
  await page.getByRole('link', { name: 'Next →', exact: true }).click();
  await expect(page).toHaveURL(/severity=high&status=Open&page=2/);
  const second = await page.locator('tbody tr').evaluateAll(rows => rows.map(row => row.dataset.reportId));
  expect(new Set([...first, ...second]).size).toBe(first.length + second.length);
  expect(inserted.every(id => first.includes(id) || second.includes(id))).toBe(true);
  await page.getByRole('link', { name: 'Remove severity filter: high', exact: true }).click();
  await expect(page).toHaveURL(/\/?status=Open$/);
  await expect(page.locator('#filter-severity')).toHaveValue('');
  await expect(page.locator('.pagination')).toContainText('Page 1');
});

test.describe('Native workflow', () => {
  test.use({ javaScriptEnabled: false });
  test('Core creation, stored guidance and status confirmation work without JavaScript', async ({ page }) => {
    await page.goto('/reports/new');
    await page.locator('#title').fill('Native form acceptance');
    await page.locator('#severity').selectOption('high');
    await page.getByRole('button', { name: 'Create report', exact: true }).click();
    await expect(page.getByRole('heading', { name: 'Native form acceptance', exact: true })).toBeVisible();
    await expect(page.locator('#completeness-score')).toHaveText('29%');
    await page.locator('#status').selectOption('In progress');
    await page.getByRole('button', { name: 'Update status', exact: true }).click();
    await expect(page.locator('.notice')).toContainText('Status updated to In progress');
  });
});
