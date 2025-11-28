import { test, expect } from '@playwright/test';
import { ProfilePage } from '../ui/pages/profilePage';
import hooks  from '../ui/utils/hooks';
import pages from '../ui/utils/pages';

let profilePage: ProfilePage;

test.beforeEach(async ({ page }) => {
    // await page.goto(pages.profile);
    // profilePage = new ProfilePage(page);
    profilePage = await hooks.beforeEach(page, ProfilePage, pages.profile);
});

test.describe('Profile - Dynamic Page Object Model', () => {
    test('Check logged in', async () => {
        expect (await profilePage.getUserEmail()).toBe(process.env.EMAIL!);
    });
});
