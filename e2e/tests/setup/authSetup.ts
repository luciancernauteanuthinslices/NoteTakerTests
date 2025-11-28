import { Page, test as setup } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import { LoginPage } from '../../ui/pages/loginPage';
import uiPages from '../../ui/utils/uiPages';

const authDir = path.resolve(__dirname, '../../data/auth');
const adminFile = path.join(authDir, 'admin.json');
const userFile = path.join(authDir, 'user.json');

setup.beforeAll(() => {
  fs.mkdirSync(authDir, { recursive: true });
});
setup.describe.configure({ mode: 'parallel' }); //if the app supports parallel login

async function doLogin(page: Page, email: string, password: string): Promise<void> {
  const baseUrl = setup.info().project.use.baseURL as string;
  const loginPage = new LoginPage(page);
  await page.goto(baseUrl + uiPages.loginPage);
  await loginPage.doLogin(email, password);
  await loginPage.checkLoggedIn();
}

setup('Authenticate as admin', { tag: '@multirole' }, async ({ page }) => {
  const email = process.env.ADMIN_EMAIL ?? process.env.EMAIL!;
  const password = process.env.ADMIN_PASSWORD ?? process.env.PASSWORD!;
  await doLogin(page, email, password);
  await page.context().storageState({ path: adminFile });
});

setup('Authenticate as user', { tag: '@multirole' }, async ({ page }) => {
  const email = process.env.EMAIL ?? process.env.EMAIL!;
  const password = process.env.PASSWORD ?? process.env.PASSWORD!;
  await doLogin(page, email, password);
  await page.context().storageState({ path: userFile });
});
