import { defineConfig, devices } from '@playwright/test';
export default defineConfig({ testDir: './e2e', retries: 1, reporter: [['list'], ['html', { outputFolder: 'playwright-report', open: 'never' }]], use: { baseURL: process.env.E2E_BASE_URL || 'http://localhost:5173', trace: 'retain-on-failure' }, projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }] });
