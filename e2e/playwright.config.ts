import { defineConfig, devices } from '@playwright/test';


/**
 * Read environment variables from file.
 * https://github.com/motdotla/dotenv
 */
import dotenv from 'dotenv';
import path from 'path';

const envName = process.env.ENV ?? 'local';

const envFile =
  envName === 'prod'
    ? '.env.prod'
    : envName === 'dev'
      ? '.env.dev'
      : '.env';

dotenv.config({ path: path.resolve(__dirname, envFile) });

const e2eRoot = __dirname;
const dataDir = path.join(e2eRoot, 'data');
const storageStatePath = path.join(dataDir, 'storageState.json');
const allureResultsDir = path.join(e2eRoot, 'allure-results');
const testResultsDir = path.join(e2eRoot, 'test-results');

/**
 * See https://playwright.dev/docs/test-configuration.
 */
export default defineConfig({
  globalSetup: require.resolve('./tests/setup/globalSetup'), //single user storagestate method
  testDir: './tests',
  outputDir: testResultsDir,
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['html'], ['allure-playwright', { 
      resultsDir: allureResultsDir, 
      detail: true,
      suiteTitle: false,
      environmentInfo: {
        appEnv: process.env.ENV,
        appUrl: process.env.APP_URL,
        buildNumber: process.env.BUILD_NUMBER,
        commit: process.env.GITHUB_SHA,
        node_version: process.version,
      },
    }]
],
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    storageState: storageStatePath,                  //single user storagestate method
    baseURL: process.env.APP_URL!,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    ignoreHTTPSErrors: true, // Ignore SSL errors if necessary
    permissions: ['geolocation'], // Set necessary permissions for geolocation-based tests
    headless: !!process.env.CI,
  },

  /* Configure projects for major browsers */
  projects: [
    // using UI to login 
    // {
    //   name: 'auth-setup',
    //   testMatch: /authSetup\.ts/,
    // },
    // {
    //   name: 'chromium-auth',
    //   use: { ...devices['Desktop Chrome'] },
    //   dependencies: ['auth-setup'],
    // },

    // using API to login 
    // {
    //   name: 'api-auth-setup',
    //   testMatch: /apiAuthSetup\.ts/
    // },
    // {
    //   name: 'chromium-api-auth',
    //   use: { ...devices['Desktop Chrome'] },
    //   dependencies: ['api-auth-setup'],
    // },
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        // Load ad blocker extension to prevent ad overlays from interfering with tests
        // Extensions only work in non-headless mode
        headless: true, // Explicitly set to false for extensions to work
      }
    },

    // {
    //   name: 'firefox',
    //   use: { ...devices['Desktop Firefox'] },
    // },

    // {
    //   name: 'webkit',
    //   use: { ...devices['Desktop Safari'] },
    // },

    /* Test against mobile viewports. */
    // {
    //   name: 'Mobile Chrome',
    //   use: { ...devices['Pixel 5'] },
    // },
    // {
    //   name: 'Mobile Safari',
    //   use: { ...devices['iPhone 12'] },
    // },

    /* Test against branded browsers. */
    // {
    //   name: 'Microsoft Edge',
    //   use: { ...devices['Desktop Edge'], channel: 'msedge' },
    // },
    // {
    //   name: 'Google Chrome',
    //   use: { ...devices['Desktop Chrome'], channel: 'chrome' },
    // },
  ],

  /* Run your local dev server before starting the tests */
  // webServer: {
  //   command: 'npm run start',
  //   url: 'http://localhost:3000',
  //   reuseExistingServer: !process.env.CI,
  // },
});
