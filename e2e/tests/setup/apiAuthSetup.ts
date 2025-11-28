import { expect, test as setup } from '@playwright/test';
import apiEndpoints from '../../ui/utils/apiEndpoints';
import fs from 'fs';

const authDir = 'data/auth';
const apiAdminFile = `${authDir}/api-admin.json`;
const apiUserFile = `${authDir}/api-user.json`;
const apiBaseUrl = process.env.API_URL!;

setup.beforeAll(() => {
    fs.mkdirSync(authDir, { recursive: true });
});

setup('authenticate as admin using api request', async ({ request }) => {
    // Send authentication request. Replace with your own.
    console.log(apiBaseUrl + apiEndpoints.account.login);

    const response = await request.post(apiBaseUrl + apiEndpoints.account.login, {
        form: {
            email: process.env.ADMIN_EMAIL!,
            password: process.env.ADMIN_PASSWORD!,
        }
    });

    console.log('Status:', response.status());
    expect(response.ok()).toBeTruthy();

    await request.storageState({ path: apiAdminFile });
});

setup('authenticate as normal user using api request', async ({ request }) => {
    // Send authentication request. Replace with your own.

    const response = await request.post(apiBaseUrl + apiEndpoints.account.login, {
        form: {
            email: process.env.EMAIL!,
            password: process.env.PASSWORD!,
        }
    });
    console.log(apiBaseUrl + apiEndpoints.account.login);
    const responseBody = await response.json();
    console.log(responseBody.data.token);
    await request.storageState({ path: apiUserFile });
});