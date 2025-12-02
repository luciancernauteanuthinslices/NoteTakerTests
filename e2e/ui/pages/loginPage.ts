import { Page, Locator } from '@playwright/test';
import messages from '../utils/messages';

export class LoginPage {
  readonly page: Page;

  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly loginButton: Locator;
  readonly forgotPasswordLink: Locator;
  readonly loginWithGoogleLink: Locator;
  readonly loginWithLinkedInLink: Locator;
  readonly createFreeAccountLink: Locator;
  readonly homePageTitle: Locator;
  readonly alertMessage: Locator;

  constructor(page: Page) {
    this.page = page;

    this.emailInput = page.locator('#email');
    this.passwordInput = page.locator('#password');
    this.loginButton = page.getByRole('button', { name: 'Login' });
    this.forgotPasswordLink = page.getByRole('link', { name: 'Forgot password' });
    this.loginWithGoogleLink = page.getByRole('link', { name: 'Login with Google' });
    this.loginWithLinkedInLink = page.getByRole('link', { name: 'Login with LinkedIn' });
    this.createFreeAccountLink = page.getByRole('link', { name: 'Create a free account!' });
    this.homePageTitle = page.locator('a[data-testid="home"]');
    this.alertMessage = page.locator('[data-testid="alert-message"]');
  }

  async doLogin(email: string, password: string): Promise<void> {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }

  async checkLoggedIn(): Promise<boolean> {
    // Wait for navigation to complete and home element to be visible
    await this.homePageTitle.waitFor({ state: 'visible', timeout: 30000 });
    const text = await this.homePageTitle.innerText();
    return text.includes('MyNotes');
  }

  async checkInvalidCredentials(): Promise<boolean> {
    if (await this.alertMessage.innerText() === messages.login.invalid) {
      return true;
    } 
    return false;
  }


}
