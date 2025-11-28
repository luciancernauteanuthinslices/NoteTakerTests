import { test as apiTest, expect } from '../ui/fixtures/login-with-api-token-fixture';
import notesApi, { NoteData } from '../ui/api/requests/notes-api';

apiTest.describe.configure({ mode: 'serial' });

let createdNote: NoteData;

apiTest.describe('Notes - Fixture & API', () => {
    // apiContext is now provided by the fixture - just destructure it in the test
    apiTest('Create note via API, verify ID, then delete', async ({ apiContext }) => {
        // Step 1: Create a new note via API
        const createNoteResponse = await notesApi.createNote(
            apiContext,
            'Test Note from API',
            'This is a test note created via API',
            'Work'
        );

        expect(createNoteResponse.success).toBe(true);
        expect(createNoteResponse.status).toBe(200);
        createdNote = createNoteResponse.data;

        // Step 2: Verify the note ID exists
        console.log(`Created note with ID: ${createdNote.id}`);
        expect(createdNote.id).toBeTruthy();
        expect(createdNote.title).toBe('Test Note from API');
        expect(createdNote.category).toBe('Work');

        // Step 3: Delete the note using the note ID
        const deleteNoteResponse = await notesApi.deleteNoteById(apiContext, createdNote.id);
        
        expect(deleteNoteResponse.success).toBe(true);
        expect(deleteNoteResponse.status).toBe(200);
        console.log(`Successfully deleted note with ID: ${createdNote.id}`);
    });

    //Get user profile 
    apiTest('Get user profile', async ({ apiContext }) => {
        const getUserProfileResponse = await notesApi.getUserProfile(apiContext);
        expect(getUserProfileResponse.success).toBe(true);
        expect(getUserProfileResponse.status).toBe(200);
        console.log(`Successfully got user profile: ${getUserProfileResponse.data.id}`);
        expect(getUserProfileResponse.data.id).toBeTruthy();
      
    });
});