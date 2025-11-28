import { Page, Locator } from '@playwright/test';
import pages from '../utils/pages';

export class HomePage {
  readonly page: Page;

  //navigation section
  readonly homeLink: Locator;
  readonly profileLink: Locator;
  readonly logoutButton: Locator;

  //search section
  readonly searchInput: Locator;
  readonly searchButton: Locator;

  //filters section
  readonly allFilterButton: Locator;
  readonly homeFilterButton: Locator;
  readonly workFilterButton: Locator;
  readonly personalFilterButton: Locator;

  //note form
  readonly addNoteButton: Locator;
  readonly categorySelect: Locator;
  readonly noteTitleInput: Locator;
  readonly noteDescriptionInput: Locator;
  readonly createNoteButton: Locator;
  readonly emptyStateHeading: Locator;
  readonly modalTitle: Locator;

  //note list section
  readonly notesList: Locator;
  readonly singleNoteCard: Locator;
  readonly viewNoteButton: Locator;
  readonly editNoteButton: Locator;
  readonly deleteNoteButton: Locator;
  readonly confirmDeleteButton: Locator;
  readonly checkCompleteNote: Locator;
  readonly cardTitle: Locator;

  constructor(page: Page) {
    this.page = page;

    //navigation section
    this.homeLink = page.getByTestId('home');
    this.profileLink = page.getByTestId('profile');
    this.logoutButton = page.getByTestId('logout');

    //search section
    this.searchInput = page.getByTestId('search-input');
    this.searchButton = page.getByTestId('search-btn');

    //filters section
    this.allFilterButton = page.getByTestId('category-all');
    this.homeFilterButton = page.getByTestId('category-home');
    this.workFilterButton = page.getByTestId('category-work');
    this.personalFilterButton = page.getByTestId('category-personal');

    //note form
    this.modalTitle = page.locator('.modal-title');
    this.addNoteButton = page.getByTestId('add-new-note');
    this.categorySelect = page.getByTestId('note-category');
    this.noteTitleInput = page.getByTestId('note-title');
    this.noteDescriptionInput = page.getByTestId('note-description');
    this.createNoteButton = page.getByTestId('note-submit');
    this.emptyStateHeading = page.getByTestId('no-notes-message');

    //note card list section
    this.notesList = page.getByTestId('notes-list');
    this.singleNoteCard = page.getByTestId('note-card');
    this.viewNoteButton = page.getByTestId('note-view');
    this.editNoteButton = page.getByTestId('note-edit');

    this.deleteNoteButton = page.getByTestId('note-delete');
    this.confirmDeleteButton = page.getByTestId('note-delete-confirm');

    this.checkCompleteNote = page.getByTestId('toggle-note-switch');
    this.cardTitle = page.getByTestId('note-title');
    

  }

  async goto(): Promise<void> {
    await this.page.goto(pages.homePage);
  }

  async logout(): Promise<void> {
      await this.logoutButton.click();
    }

  async isLoaded(): Promise<boolean> {
    await this.page.waitForURL(pages.homePage);
    return this.homeLink.isVisible();
  }

  async openProfile(): Promise<void> {
    await this.profileLink.click();
  }

  async search(term: string): Promise<void> {
    await this.searchInput.fill(term);
    await this.searchButton.click();
  }

  async checkNote(): Promise<void> {
    await this.checkCompleteNote.click();
  }

  async noteSelectCategory(category: 'Home' | 'Work' | 'Personal'): Promise<void> {
  if (category === 'Home') {
    await this.categorySelect.selectOption({ value: 'Home' });
  } else if (category === 'Work') {
    await this.categorySelect.selectOption({ value: 'Work' });
  } else {
    await this.categorySelect.selectOption({ value: 'Personal' });
  }
}

  async filterByCategory(category: 'All' | 'Home' | 'Work' | 'Personal'): Promise<void> {
    switch (category) {
      case 'All':
        await this.allFilterButton.click();
        break;
      case 'Home':
        await this.homeFilterButton.click();
        break;
      case 'Work':
        await this.workFilterButton.click();
        break;
      case 'Personal':
        await this.personalFilterButton.click();
        break;
    }
  }
    
  async clickAddNote(): Promise<void> {
    // Use force click to bypass any ad overlays
    await this.addNoteButton.click({ force: true });
    // Wait for modal to appear
    await this.modalTitle.waitFor({ state: 'visible', timeout: 5000 });
  }

  async hasEmptyStateMessage(): Promise<boolean> {
    return this.emptyStateHeading.isVisible();
  }

  async fillNote(category: 'Home' | 'Work' | 'Personal', title: string, description: string): Promise<void> {
    await this.clickAddNote();
    await this.noteSelectCategory(category);
    await this.noteTitleInput.fill(title);
    await this.noteDescriptionInput.fill(description);
    // Use force click to bypass any ad overlays
    await this.createNoteButton.click({ force: true });
  }

  async getCardTitle(): Promise<string> {
    // Get the title from the first note card header
    const firstCard = this.singleNoteCard.first();
    // The card title is in the card-title element within the note card
    return firstCard.locator('.card-title').innerText();
  }

  //for each note card exist, click on delete button
  async cleanAllNotes(): Promise<void> {
    // Delete notes one by one - always delete the first one since the list shifts after each delete
    let attempts = 0;
    const maxAttempts = 10;
    
    while ((await this.singleNoteCard.count()) > 0 && attempts < maxAttempts) {
      attempts++;
      const initialCount = await this.singleNoteCard.count();
      
      // Use force click to bypass any ad overlays
      await this.deleteNoteButton.first().click({ force: true });
      
      try {
        await this.confirmDeleteButton.waitFor({ state: 'visible', timeout: 3000 });
        await this.confirmDeleteButton.click({ force: true });
        await this.page.waitForTimeout(500);
      } catch {
        console.log('Confirm button not found, skipping cleanup');
        break;
      }
      
      const newCount = await this.singleNoteCard.count();
      if (newCount >= initialCount) {
        console.log('Note count did not decrease, stopping cleanup');
        break;
      }
    }
  }
}

