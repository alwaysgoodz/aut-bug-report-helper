const { test, expect } = require('@playwright/test');
const study = 'http://127.0.0.1:8790';

test('TEST-ONLY study pilot captures two conditions and exposes a real seeded fixture', async ({ page }) => {
  await page.goto(study);
  await expect(page.getByText('TEST-ONLY PILOT - not human evidence')).toBeVisible();
  await page.getByRole('link', { name: 'P01', exact: true }).click();
  await page.getByRole('checkbox').check();
  await page.getByRole('button', { name: 'Consent and continue' }).click();
  await page.getByRole('button', { name: 'Start timed task' }).click();
  const popupReady = page.waitForEvent('popup');
  await page.getByRole('link', { name: 'Study Planner / build 1.0' }).click();
  const fixture = await popupReady;
  await fixture.locator('#fixture-filter').selectOption('Active');
  await expect(fixture.locator('#fixture-view')).toHaveText('Current view: Active');
  await expect(fixture.locator('#fixture-items li')).toHaveCount(3);
  await expect(fixture.getByText('Send project outline - Completed', { exact: true })).toBeVisible();
  await fixture.close();
  await page.locator('#body').fill('Test-only: Active view includes completed items after selecting the view.');
  await page.getByRole('button', { name: 'Submit report', exact: true }).click();
  await page.getByRole('button', { name: 'Start timed task' }).click();
  await expect(page.locator('form[data-completeness]')).toBeVisible();
  await page.locator('#title').fill('Urgent view includes normal items');
  await page.locator('#severity').selectOption('low');
  await expect(page.locator('#completeness-score')).toHaveText('29%');
  await page.getByRole('button', { name: 'Create report', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Both reports submitted' })).toBeVisible();
  await page.goto(study);
  await expect(page.getByText('1/4 consented; 2/8 reports; 0/8 reviewed; 0/4 complete pairs.')).toBeVisible();
});

test('TEST-ONLY guided validation retains inputs and reviewer masks explicit condition labels', async ({ page }) => {
  await page.goto(study + '/participant/P02');
  await page.getByRole('checkbox').check();
  await page.getByRole('button', { name: 'Consent and continue' }).click();
  await page.getByRole('button', { name: 'Start timed task' }).click();
  await page.locator('#title').fill('  ');
  await page.locator('#steps').fill('Keep this pilot input');
  await page.locator('#severity').selectOption('medium');
  await page.getByRole('button', { name: 'Create report', exact: true }).click();
  await expect(page.locator('#form-errors')).toBeFocused();
  await expect(page.locator('#steps')).toHaveValue('Keep this pilot input');
  await page.locator('#title').fill('Active view shows completed item');
  await page.getByRole('button', { name: 'Create report', exact: true }).click();
  await page.goto(study + '/review');
  await page.getByRole('link', { name: 'Report 1', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Report review' })).toBeVisible();
  await expect(page.locator('main')).not.toContainText('P01');
  await expect(page.locator('main')).not.toContainText('P02');
  await page.locator('input[name="reviewer"]').fill('R01');
  await page.getByRole('checkbox').check();
  for (const field of ['title', 'description', 'steps', 'expected', 'actual', 'environment', 'severity']) {
    await page.locator(`select[name="${field}"]`).selectOption('0');
  }
  await page.locator('select[name="outcome"]').selectOption('not_reproduced');
  await page.locator('input[name="clarifications"]').fill('0');
  await page.getByRole('button', { name: 'Save actual review' }).click();
  await expect(page.getByRole('heading', { name: 'Independent review queue' })).toBeVisible();
});
