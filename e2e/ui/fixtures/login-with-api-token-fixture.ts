import { test as base, APIRequestContext } from '@playwright/test';
import notesApi from '../api/requests/notes-api';

type ApiFixtures = {
    apiContext: APIRequestContext;
};

/**
 * Extended test with API authentication fixture.
 * Provides an authenticated `apiContext` that can be used for API calls.
 */
export const test = base.extend<ApiFixtures>({
    apiContext: async ({ playwright }, use) => {
        // Read env variables
        const apiUrl = process.env.API_URL;
        const email = process.env.EMAIL;
        const password = process.env.PASSWORD;

        if (!apiUrl || !email || !password) {
            throw new Error('Missing required environment variables: API_URL, EMAIL, PASSWORD');
        }
        
        console.log(`Using API URL: ${apiUrl}`);
        console.log(`Using email: ${email}`);

        // Set the base URL for all API functions
        notesApi.setApiBaseUrl(apiUrl);

        // First create context without auth for login
        const loginContext = await playwright.request.newContext({
            baseURL: apiUrl,
            extraHTTPHeaders: {
                Accept: 'application/json',
            },
        });

        // Login to get the auth token
        const loginResponse = await notesApi.login(loginContext, email, password, apiUrl);
        const authToken = loginResponse.data.token;
        console.log(`Logged in successfully, token obtained`);

        // Create authenticated API context
        const apiContext = await playwright.request.newContext({
            baseURL: apiUrl,
            extraHTTPHeaders: {
                'x-auth-token': authToken,
                Accept: 'application/json',
            },
        });

        // Provide the apiContext to the test
        await use(apiContext);

        // Cleanup: dispose the context after the test
        await apiContext.dispose();
    },
});

export { expect } from '@playwright/test';