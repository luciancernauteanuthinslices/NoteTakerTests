import { FullConfig, chromium } from '@playwright/test';
import { LoginPage } from '../../ui/pages/loginPage';
import uiPages from '../../ui/utils/uiPages';


async function globalSetup(config: FullConfig): Promise<void> {
  
  const email = process.env.EMAIL!;
  const password = process.env.PASSWORD!;
  const { baseURL, storageState } = config.projects[0].use;
  const browser = await chromium.launch({ headless: true, timeout: 10000 });
  const page = await browser.newPage();
  const loginPage = new LoginPage(page);

  await page.goto(baseURL+uiPages.loginPage);
  await loginPage.doLogin(email, password);
  await loginPage.checkLoggedIn();
  await page.context().storageState({ path: storageState as string });
  await browser.close();
}

export default globalSetup;


