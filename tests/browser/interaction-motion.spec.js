const { test, expect } = require('@playwright/test');

// Capture the UI at the real submit event, after the application's listener.
// Post-navigation DOM queries would wait for the deliberately delayed response.
async function captureSubmission(page, selector) {
  const captured = [];
  await page.exposeFunction('recordPendingUI', state => captured.push(state));
  await page.evaluate(selector => {
    document.querySelector(selector).addEventListener('submit', event => {
      const button = event.currentTarget.querySelector('button[type=submit]');
      window.recordPendingUI({ text: button.textContent, disabled: button.disabled,
        busy: button.getAttribute('aria-busy'), formBusy: button.form.getAttribute('aria-busy'),
        width: button.getBoundingClientRect().width });
    });
  }, selector);
  return captured;
}

test('Live completeness stays exact while visual progress retargets during rapid edits', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'no-preference' });
  await page.goto('/reports/new');
  await page.locator('#title').fill('Motion acceptance sample');
  await page.locator('#description').fill('A useful description');
  await page.locator('#steps').fill('1. Open settings');
  await page.locator('#environment').fill('Demo build / Chromium');
  await page.locator('#description').fill('');
  await expect(page.locator('#completeness-score')).toHaveText('43%');
  await expect(page.locator('#completeness-progress')).toHaveAttribute('value', '43');
  await expect(page.locator('#missing-fields li:visible')).toHaveCount(4);
  await expect.poll(() => page.locator('.completion-fill').evaluate(el =>
    Math.round(new DOMMatrixReadOnly(getComputedStyle(el).transform).a * 100)
  )).toBe(43);
  await expect(page.getByRole('progressbar', { name: 'Report completeness', exact: true })).toHaveAttribute('value', '43');
  await page.locator('#steps').focus();
  await expect.poll(() => page.locator('#group-02').evaluate(el =>
    getComputedStyle(el.closest('.form-section').querySelector('.section-number')).backgroundColor
  )).toBe('rgb(23, 100, 109)');
  await page.locator('#title').fill('');
  await expect(page.locator('#completeness-score')).toHaveText('29%');
  await expect.poll(() => page.locator('.completion-fill').evaluate(el =>
    Math.round(new DOMMatrixReadOnly(getComputedStyle(el).transform).a * 100)
  )).toBe(29);
});

test('Slow save shows a stable busy state, then history restores labels and usable controls', async ({ page }) => {
  await page.goto('/reports/new');
  await page.locator('#title').fill('Slow-save acceptance sample');
  await page.locator('#severity').selectOption('high');
  const button = page.getByRole('button', { name: 'Create report', exact: true });
  const originalWidth = await button.evaluate(el => el.getBoundingClientRect().width);
  const captured = await captureSubmission(page, '.report-form');
  let release;
  const gate = new Promise(resolve => { release = resolve; });
  let requests = 0;
  await page.route('**/reports', async route => {
    if (route.request().method() === 'POST') { requests++; await gate; }
    await route.continue();
  });
  await button.click({ noWaitAfter: true });
  try {
    await expect.poll(() => captured[0]).toMatchObject({ text: 'Saving report…', disabled: true, busy: 'true', formBusy: 'true' });
    expect(captured[0].width).toBeGreaterThanOrEqual(originalWidth - 1);
    await expect.poll(() => requests).toBe(1);
  } finally { release(); }
  await expect(page.getByRole('heading', { name: 'Slow-save acceptance sample', exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Update status', exact: true })).toBeDisabled();
  await page.locator('#status').selectOption('In progress');
  await expect(page.locator('#status-help')).toHaveText('Ready to change from Open to In progress. Save to confirm.');
  await expect(page.getByRole('button', { name: 'Update status', exact: true })).toBeEnabled();
  await page.locator('#status').selectOption('Open');
  await expect(page.getByRole('button', { name: 'Update status', exact: true })).toBeDisabled();
  await page.goBack();
  await expect(page.getByRole('button', { name: 'Create report', exact: true })).toBeEnabled();
  await expect(page.locator('button[aria-busy=true], form[aria-busy=true]')).toHaveCount(0);
  await expect(page.locator('#title')).toHaveValue('Slow-save acceptance sample');
  await expect(page.locator('#completeness-score')).toHaveText('29%');
});

test('Filter requests show applying feedback and browser Back restores the original action', async ({ page }) => {
  await page.goto('/');
  await page.locator('#filter-severity').selectOption('high');
  await page.locator('#filter-status').selectOption('Open');
  const captured = await captureSubmission(page, '.filters');
  let release;
  const gate = new Promise(resolve => { release = resolve; });
  await page.route('**/?severity=high&status=Open', async route => {
    await gate;
    await route.continue();
  });
  await page.getByRole('button', { name: 'Apply filters', exact: true }).click({ noWaitAfter: true });
  try {
    await expect.poll(() => captured[0]).toMatchObject({ text: 'Applying…', disabled: true, busy: 'true', formBusy: 'true' });
  } finally { release(); }
  await expect(page).toHaveURL(/severity=high&status=Open$/);
  await page.goBack();
  await expect(page.getByRole('button', { name: 'Apply filters', exact: true })).toBeEnabled();
  await expect(page.locator('button[aria-busy=true], form[aria-busy=true]')).toHaveCount(0);
});

test('Reduced motion works initially and on live preference changes without delaying feedback', async ({ page }) => {
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/reports/new');
  await page.locator('#title').fill('Reduced-motion acceptance sample');
  await page.locator('#severity').selectOption('high');
  await expect(page.locator('#completeness-score')).toHaveText('29%');
  await expect(page.locator('#completeness-progress')).toHaveAttribute('value', '29');
  expect(await page.locator('.completion-fill').evaluate(el => getComputedStyle(el).transitionDuration)).toBe('0s');
  expect(await page.evaluate(() => document.getAnimations().length)).toBe(0);
  await page.locator('.guidance-details summary').press('Enter');
  await expect(page.locator('#missing-fields li:visible')).toHaveCount(5);
  await page.emulateMedia({ reducedMotion: 'no-preference' });
  await page.locator('#steps').fill('1. Open the application');
  await page.emulateMedia({ reducedMotion: 'reduce' });
  await expect(page.locator('#completeness-score')).toHaveText('43%');
  await expect.poll(() => page.evaluate(() => document.getAnimations().length)).toBe(0);
  expect(await page.locator('.completion-fill').evaluate(el =>
    Math.round(new DOMMatrixReadOnly(getComputedStyle(el).transform).a * 100)
  )).toBe(43);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});
