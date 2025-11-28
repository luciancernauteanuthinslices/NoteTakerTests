import { test, expect } from '@playwright/test';
import { LoginPage } from '../ui/pages/loginPage';
import pages from '../ui/utils/pages';
import user from '../data/userData';


const email = process.env.EMAIL!;
const password = process.env.PASSWORD!;

let loginPage: LoginPage;

test.use({ storageState: { cookies: [], origins: [] } }); // doesn't share the logged in session
// test.use({ storageState: undefined }); // https://github.com/microsoft/playwright/issues/17396
test.describe.configure({ mode: 'serial' });

test.beforeEach(async ({ page }) => {
  await page.goto(pages.loginPage);
loginPage = new LoginPage(page);
});

test.describe('NoteTaker - Login', () => {

  test('valid credentials', async () => {
    await loginPage.doLogin(email, password);
    await loginPage.checkLoggedIn();
  });

  test('failed login - invalid username', async () => {
    const invalidUsername = user.invalidEmail;
    await loginPage.doLogin(invalidUsername, password);

    const hasErrorMessage = await loginPage.checkInvalidCredentials();
    expect(hasErrorMessage).toBeTruthy();
});

  test('failed login - invalid password', async () => {
    const invalidPassword = user.invalidPassword;
    await loginPage.doLogin(email, invalidPassword);

    const hasErrorMessage = await loginPage.checkInvalidCredentials();
    expect(hasErrorMessage).toBeTruthy();
});
});


