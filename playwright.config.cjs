const { defineConfig } = require('@playwright/test');
const python = process.env.BUGREPORT_PYTHON || 'python';
if (!/^[\w .:/\\-]+$/.test(python)) throw new Error('BUGREPORT_PYTHON contains unsupported command characters');

module.exports = defineConfig({
  testDir: './tests/browser',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 15000,
  globalTimeout: 180000,
  expect: { timeout: 4000 },
  reporter: [['list'], ['json', { outputFile: 'test-results/browser-results.json' }], ['html', { open: 'never' }]],
  use: {
    baseURL: 'http://127.0.0.1:8780',
    browserName: 'chromium',
    channel: process.env.BUGREPORT_BROWSER_CHANNEL || undefined,
    viewport: { width: 1440, height: 1000 },
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },
  webServer: [{
    command: `"${python}" -m tools.e2e_server`,
    url: 'http://127.0.0.1:8780/health',
    reuseExistingServer: false,
    timeout: 15000,
    stdout: 'pipe',
    stderr: 'pipe',
  }, {
    command: `"${python}" -m tools.study_e2e_server`,
    url: 'http://127.0.0.1:8790/health',
    reuseExistingServer: false,
    timeout: 15000,
    stdout: 'pipe',
    stderr: 'pipe',
  }],
});
