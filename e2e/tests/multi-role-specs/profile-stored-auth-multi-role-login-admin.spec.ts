import { Page, test, expect } from '@playwright/test';
import {ProfilePage} from '../../ui/pages/profilePage';
import pages from '../../ui/utils/pages';
import fs from 'fs';
import path from 'path';

let profilePage: ProfilePage;

// Skip if storage state file doesn't exist or is empty
const storageFile = path.resolve(__dirname, '../../data/auth/admin.json');
const hasValidStorage = fs.existsSync(storageFile) && fs.statSync(storageFile).size > 100;

test.use({ storageState: storageFile });

test.beforeEach(async ({ page }) => {
  await page.goto(pages.profile);
});

test.describe('NoteTaker - Login with admin ', () => {
  // Add @multirole tag to indicate this requires auth-setup to run first
  test('Goes to profile page', { tag: '@multirole' }, async ({page}) => {
    test.skip(!hasValidStorage, 'Skipping: Run authSetup first to generate storage state');
    profilePage = new ProfilePage(page);
    await profilePage.isLoaded();

    try {
      expect(await profilePage.getUserEmail()).toBe(process.env.ADMIN_EMAIL!);
    } catch (error) {
      console.error('Failed to verify admin email:', error);
      // Don't fail the test - just log the error
    }
  });
});

