import { expect } from '@playwright/test';
import { test } from '../ui/fixtures/notes-fixtures';

// Use the custom notes fixture test which provides homePage with cleanup
test.describe('NoteTaker - Profile - Dynamic POM', () => {
  // NOTE: This test is skipped because the practice testing site has intrusive ads
  // that intercept button clicks and cause navigation away from the app.
  // Options to fix:
  // 1. Load the ad blocker extension from e2e/extensions/adBlocker/
  // 2. Use API to create notes instead of UI
  // 3. Test on a staging environment without ads
  test.skip('Add a note with fixtures', async ({ homePage }) => {
    await homePage.isLoaded();
    await homePage.fillNote('Personal', 'SuperTitle1', 'SuperDescription1');
    
    // Wait for modal to close and note card to appear
    await homePage.modalTitle.waitFor({ state: 'hidden', timeout: 10000 });
    await homePage.singleNoteCard.first().waitFor({ state: 'visible', timeout: 10000 });
    
    // Verify note was created
    expect(await homePage.getCardTitle()).toContain('SuperTitle1');
  });
});


