import { test, expect, request } from '@playwright/test';
import { HomePage } from '../ui/pages/homePage';
import pages from '../ui/utils/pages';
import hooks from '../ui/utils/hooks';
import {test as notesFixtures} from '../ui/fixtures/notes-fixtures';
import { faker } from '@faker-js/faker';

let homePage: HomePage;

// test.use({ storageState: { cookies: [], origins: [] } }); // doesn't share the logged in session
// test.use({ storageState: undefined }); // https://github.com/microsoft/playwright/issues/17396
// test.describe.configure({ mode: 'serial' });

test.beforeEach(async ({ page }) => {
  homePage = await hooks.beforeEach(page, HomePage, pages.homePage);
  });

test.describe('NoteTaker - Profile - Dynamic POM', () => {
  notesFixtures('Add a note with fixtures', async ({homePage }) => {

    await homePage.isLoaded();
  
    // await homePage.checkCompleteNote.click();

    await homePage.fillNote('Personal', 'SuperTitle1', 'SuperDescription1');

  
    // await homePage.filterByCategory('Home');

  });
});


