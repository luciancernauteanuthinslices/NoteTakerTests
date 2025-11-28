import { Page, test, expect } from '@playwright/test';
import {ProfilePage} from '../../ui/pages/profilePage';
import pages from '../../ui/utils/pages';

let profilePage: ProfilePage;

test.use({ storageState: 'data/auth/admin.json' });

test.beforeEach(async ({ page }) => {
  await page.goto(pages.profile);
});

test.describe('NoteTaker - Login with admin ', () => {
  test('Goes to profile page',  {tag: '@multirole'}, async ({page}) => {
     profilePage = new ProfilePage(page);
    await profilePage.isLoaded();
    expect (await profilePage.getUserEmail()).toBe(process.env.ADMIN_EMAIL!);
  });

});


