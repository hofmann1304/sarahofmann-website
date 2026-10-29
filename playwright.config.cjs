const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests/browser',
  workers: 2,
  retries: 0,
  reporter: 'list',
  outputDir: 'tmp/browser-results',
  use: {
    baseURL: 'http://127.0.0.1:8765',
    browserName: 'chromium',
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure',
  },
  webServer: {
    command: 'python scripts/serve_site.py --port 8765',
    url: 'http://127.0.0.1:8765',
    reuseExistingServer: false,
    stderr: 'ignore',
    timeout: 30000,
  },
});
