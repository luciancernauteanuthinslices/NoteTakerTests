import { Page, Locator } from '@playwright/test';
import pages from '../utils/pages';

export class ProfilePage {
  readonly page: Page;

  readonly homeLink: Locator;
  readonly profileLink: Locator;
  readonly logoutButton: Locator;

  readonly accountDetailsTab: Locator;
  readonly changePasswordTab: Locator;

  readonly userIdInput: Locator;
  readonly userEmailInput: Locator;
  readonly fullNameInput: Locator;
  readonly phoneNumberInput: Locator;
  readonly companyNameInput: Locator;
  readonly updateProfileButton: Locator;
  readonly deleteAccountButton: Locator;

  readonly currentPasswordInput: Locator;
  readonly newPasswordInput: Locator;
  readonly confirmPasswordInput: Locator;
  readonly updatePasswordButton: Locator;

  constructor(page: Page) {
    this.page = page;

    this.homeLink = page.locator('[data-testid="home"]');
    this.profileLink = page.locator('[data-testid="profile"]');
    this.logoutButton = page.locator('[data-testid="logout"]');

    this.accountDetailsTab = page.locator('[data-testid="account-details"]');
    this.changePasswordTab = page.locator('[data-testid="change-password"]');

    this.userIdInput = page.locator('#user-id');
    this.userEmailInput = page.locator('#user-email');
    this.fullNameInput = page.locator('[data-testid="user-name"]');
    this.phoneNumberInput = page.locator('[data-testid="user-phone"]');
    this.companyNameInput = page.locator('[data-testid="user-company"]');
    this.updateProfileButton = page.locator('[data-testid="update-profile"]');
    this.deleteAccountButton = page.locator('[data-testid="delete-account"]');

    this.currentPasswordInput = page.locator('[data-testid="current-password"]');
    this.newPasswordInput = page.locator('[data-testid="new-password"]');
    this.confirmPasswordInput = page.locator('[data-testid="confirm-password"]');
    this.updatePasswordButton = page.locator('[data-testid="update-password"]');
  }

  async goto(): Promise<void> {
    await this.page.goto(pages.profile);
  }

  async isLoaded(): Promise<boolean> {
    await this.page.waitForURL('**/notes/app/profile*');
    return this.accountDetailsTab.isVisible();
  }

  async openAccountDetails(): Promise<void> {
    await this.accountDetailsTab.click();
  }

  async openChangePassword(): Promise<void> {
    await this.changePasswordTab.click();
  }

  async updateProfile(fullName: string, phone: string, company: string): Promise<void> {
    await this.openAccountDetails();
    await this.fullNameInput.fill(fullName);
    await this.phoneNumberInput.fill(phone);
    await this.companyNameInput.fill(company);
    await this.updateProfileButton.click();
  }

  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await this.openChangePassword();
    await this.currentPasswordInput.fill(currentPassword);
    await this.newPasswordInput.fill(newPassword);
    await this.confirmPasswordInput.fill(newPassword);
    await this.updatePasswordButton.click();
  }

  async deleteAccount(): Promise<void> {
    await this.deleteAccountButton.click();
  }

  async getUserId(): Promise<string> {
    return this.userIdInput.inputValue();
  }

  async getUserEmail(): Promise<string> {
    return this.userEmailInput.inputValue();
  }
}

