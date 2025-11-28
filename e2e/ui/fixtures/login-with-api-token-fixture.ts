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
        const baseAPIUrl = process.env.BASE_API_URL || process.env.API_URL;
        const email = process.env.EMAIL;
        const password = process.env.PASSWORD;

        console.log(`Using API URL: ${baseAPIUrl}`);
        console.log(`Using email: ${email}`);

        if (!baseAPIUrl || !email || !password) {
            throw new Error('Missing required environment variables: BASE_API_URL/API_URL, EMAIL, PASSWORD');
        }

        // Set the base URL for all API functions
        notesApi.setApiBaseUrl(baseAPIUrl);

        // First create context without auth for login
        const loginContext = await playwright.request.newContext({
            baseURL: baseAPIUrl,
            extraHTTPHeaders: {
                Accept: 'application/json',
            },
        });

        // Login to get the auth token
        const loginResponse = await notesApi.login(loginContext, email, password, baseAPIUrl);
        const authToken = loginResponse.data.token;
        console.log(`Logged in successfully, token obtained`);

        // Create authenticated API context
        const apiContext = await playwright.request.newContext({
            baseURL: baseAPIUrl,
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