import { Page, Locator } from '@playwright/test';

export class RegistrationPage {
  readonly page: Page;

  readonly emailInput: Locator;
  readonly nameInput: Locator;
  readonly passwordInput: Locator;
  readonly confirmPasswordInput: Locator;
  readonly registerButton: Locator;
  readonly registerWithGoogleLink: Locator;
  readonly registerWithLinkedInLink: Locator;
  readonly loginHereLink: Locator;

  constructor(page: Page) {
    this.page = page;

    this.emailInput = page.locator('#email');
    this.nameInput = page.locator('#name');
    this.passwordInput = page.locator('#password');
    this.confirmPasswordInput = page.locator('#confirmPassword');
    this.registerButton = page.getByRole('button', { name: 'Register' });
    this.registerWithGoogleLink = page.getByRole('link', { name: 'Register with Google' });
    this.registerWithLinkedInLink = page.getByRole('link', { name: 'Register with LinkedIn' });
    this.loginHereLink = page.getByRole('link', { name: 'Log in here!' });
  }

  async registerNewUser(
    email: string,
    name: string,
    password: string,
    confirmPassword: string,
  ): Promise<void> {
    await this.emailInput.fill(email);
    await this.nameInput.fill(name);
    await this.passwordInput.fill(password);
    await this.confirmPasswordInput.fill(confirmPassword);
    await this.registerButton.click();
  }
}
