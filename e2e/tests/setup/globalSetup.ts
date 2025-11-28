import { FullConfig, chromium } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import { LoginPage } from '../../ui/pages/loginPage';
import uiPages from '../../ui/utils/uiPages';

async function loginAndSaveState(baseURL: string, email: string, password: string, statePath: string): Promise<void> {
  const browser = await chromium.launch({ headless: true, timeout: 10000 });
  const page = await browser.newPage();
  const loginPage = new LoginPage(page);

  await page.goto(baseURL + uiPages.loginPage);
  await loginPage.doLogin(email, password);
  await loginPage.checkLoggedIn();
  await page.context().storageState({ path: statePath });
  await browser.close();
}

async function globalSetup(config: FullConfig): Promise<void> {
  const { baseURL, storageState } = config.projects[0].use;
  const e2eRoot = path.resolve(__dirname, '../../');
  const authDir = path.join(e2eRoot, 'data', 'auth');
  fs.mkdirSync(authDir, { recursive: true });

  const email = process.env.EMAIL!;
  const password = process.env.PASSWORD!;
  const adminEmail = process.env.ADMIN_EMAIL ?? email;
  const adminPassword = process.env.ADMIN_PASSWORD ?? password;
  const userStatePath = path.join(authDir, 'user.json');
  const adminStatePath = path.join(authDir, 'admin.json');

  // Primary user storage (used by config `use.storageState`)
  await loginAndSaveState(baseURL as string, email, password, storageState as string);

  // Copy primary state for the regular user fixture
  fs.copyFileSync(storageState as string, userStatePath);

  // Create admin storage if distinct credentials are provided
  if (adminEmail === email && adminPassword === password) {
    fs.copyFileSync(storageState as string, adminStatePath);
  } else {
    await loginAndSaveState(baseURL as string, adminEmail, adminPassword, adminStatePath);
  }
}

export default globalSetup;

