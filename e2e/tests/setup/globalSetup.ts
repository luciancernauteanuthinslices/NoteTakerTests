import { FullConfig, chromium } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import { LoginPage } from '../../ui/pages/loginPage';
import { RegistrationPage } from '../../ui/pages/registrationPage';
import { generateRegistrationData, GeneratedUser } from '../../data/userGenerator';
import uiPages from '../../ui/utils/uiPages';

const E2E_ROOT = path.resolve(__dirname, '../../');

// Determine env file based on ENV variable (same logic as playwright.config.ts)
const envName = process.env.ENV ?? 'local';
const envFileName =
  envName === 'prod'
    ? '.env.prod'
    : envName === 'dev'
      ? '.env.dev'
      : '.env';

const ENV_FILE_PATH = path.join(E2E_ROOT, envFileName);

/**
 * Updates the .env file with new user credentials.
 * Preserves other environment variables.
 */
function updateEnvFile(email: string, password: string): void {
  let envContent = '';
  
  if (fs.existsSync(ENV_FILE_PATH)) {
    envContent = fs.readFileSync(ENV_FILE_PATH, 'utf-8');
  }
  
  // Parse existing env vars
  const envLines = envContent.split('\n');
  const envMap = new Map<string, string>();
  
  for (const line of envLines) {
    const trimmed = line.trim();
    if (trimmed && !trimmed.startsWith('#') && trimmed.includes('=')) {
      const [key, ...valueParts] = trimmed.split('=');
      envMap.set(key.trim(), valueParts.join('=').trim());
    }
  }
  
  // Update EMAIL and PASSWORD
  envMap.set('EMAIL', email);
  envMap.set('PASSWORD', password);
  
  // Rebuild .env content
  const newEnvContent = Array.from(envMap.entries())
    .map(([key, value]) => `${key}=${value}`)
    .join('\n');
  
  fs.writeFileSync(ENV_FILE_PATH, newEnvContent + '\n');
  
  // Also update process.env for current run
  process.env.EMAIL = email;
  process.env.PASSWORD = password;
  
  console.log(`✅ Updated ${envFileName} with new user: ${email}`);
}

/**
 * Registers a new user via the UI.
 */
async function registerNewUser(
  baseURL: string,
  user: GeneratedUser & { confirmPassword: string }
): Promise<void> {
  const browser = await chromium.launch({ headless: true, timeout: 30000 });
  const page = await browser.newPage();
  const registrationPage = new RegistrationPage(page);

  console.log(`📝 Registering new user: ${user.email}`);
  
  await page.goto(baseURL + uiPages.registerPage);
  
  await registrationPage.registerNewUser(
    user.email,
    user.name,
    user.password,
    user.confirmPassword
  );
  
  // Wait for registration to complete - look for success message or redirect
  // The success message contains "User account created successfully"
  const successMessage = page.locator('text=User account created successfully');
  const errorMessage = page.locator('[data-testid="alert-message"]');
  
  // Wait for either redirect to login OR success message (longer timeout for slow API)
  try {
    await Promise.race([
      page.waitForURL('**/login**', { timeout: 30000 }),
      successMessage.waitFor({ state: 'visible', timeout: 30000 }),
      errorMessage.waitFor({ state: 'visible', timeout: 30000 })
    ]);
  } catch {
    console.log(`⚠️  Timeout waiting for registration response`);
    await page.screenshot({ path: 'debug-registration.png' });
    console.log(`📸 Screenshot saved to debug-registration.png`);
  }
  
  // Check current state
  const currentUrl = page.url();
  console.log(`📍 URL after registration: ${currentUrl}`);
  
  // Check for success
  if (await successMessage.isVisible({ timeout: 2000 }).catch(() => false)) {
    console.log(`✅ Registration success message detected`);
  } else if (await errorMessage.isVisible({ timeout: 2000 }).catch(() => false)) {
    const alertText = await errorMessage.innerText();
    console.log(`📋 Alert message: ${alertText}`);
    
    // Check if it's an error
    if (alertText.toLowerCase().includes('error') || alertText.includes('already') || alertText.toLowerCase().includes('invalid')) {
      await browser.close();
      throw new Error(`Registration failed: ${alertText}`);
    }
  } else if (currentUrl.includes('/register')) {
    await page.screenshot({ path: 'debug-registration.png' });
    await browser.close();
    throw new Error('Registration did not complete - no success or error message found');
  }
  
  await browser.close();
  console.log(`✅ User registered successfully: ${user.email}`);
}

/**
 * Logs in and saves storage state.
 */
async function loginAndSaveState(
  baseURL: string,
  email: string,
  password: string,
  statePath: string
): Promise<void> {
  const browser = await chromium.launch({ headless: true, timeout: 30000 });
  const page = await browser.newPage();
  const loginPage = new LoginPage(page);

  console.log(`🔐 Logging in as: ${email}`);
  
  await page.goto(baseURL + uiPages.loginPage);
  await loginPage.doLogin(email, password);
  
  // Debug: check current URL and any error messages
  await page.waitForTimeout(2000); // Give page time to respond
  console.log(`📍 URL after login attempt: ${page.url()}`);
  
  // Check for error message
  const alertMessage = page.locator('[data-testid="alert-message"]');
  if (await alertMessage.isVisible({ timeout: 3000 }).catch(() => false)) {
    const alertText = await alertMessage.innerText();
    console.log(`⚠️  Alert message: ${alertText}`);
    if (alertText.includes('Incorrect') || alertText.includes('Invalid')) {
      throw new Error(`Login failed: ${alertText}`);
    }
  }
  
  await loginPage.checkLoggedIn();
  await page.context().storageState({ path: statePath });
  await browser.close();
  
  console.log(`✅ Storage state saved to: ${statePath}`);
}

async function globalSetup(config: FullConfig): Promise<void> {
  const { baseURL, storageState } = config.projects[0].use;
  const authDir = path.join(E2E_ROOT, 'data', 'auth');
  fs.mkdirSync(authDir, { recursive: true });

  console.log('\n' + '='.repeat(60));
  console.log(`🚀 Global Setup: Creating fresh user for test run (ENV: ${envName})`);
  console.log(`   Using env file: ${envFileName}`);
  console.log('='.repeat(60) + '\n');

  
  // Leave this block active (and keep the static user block commented) 
  // when you want a fresh, unique user for every test run.

  //====================================================
  // Option A: Auto-register a new user for each test run with Faker
  const newUser = generateRegistrationData();
  
  console.log(`Generated user: ${newUser.email}`);
  
  // Register the new user
  await registerNewUser(baseURL as string, newUser);
  
  // Update .env with new credentials
  updateEnvFile(newUser.email, newUser.password);
  
  // Login and save storage state
  await loginAndSaveState(
    baseURL as string,
    newUser.email,
    newUser.password,
    storageState as string
  );
//====================================================


// Comment out or remove the Option A block above.
// Uncomment the static user block below.
// Ensure EMAIL and PASSWORD are set in the correct env file (.env, .env.dev, .env.prod).


//====================================================

// // OPTION B: Use static user from environment (comment out Option A above)

//   console.log(`Logging in with static user: ${process.env.EMAIL}`);
//   await loginAndSaveState(
//   baseURL as string,
//   process.env.EMAIL as string,
//   process.env.PASSWORD as string,
//   storageState as string
// );

//====================================================


  // Copy primary state for the regular user fixture
  const userStatePath = path.join(authDir, 'user.json');
  fs.copyFileSync(storageState as string, userStatePath);

  // Handle admin user (use existing admin credentials from env only)
  const adminEmail = process.env.ADMIN_EMAIL;
  const adminPassword = process.env.ADMIN_PASSWORD;
  const adminStatePath = path.join(authDir, 'admin.json');

  if (adminEmail && adminPassword) {
    // Use existing admin credentials
    await loginAndSaveState(baseURL as string, adminEmail, adminPassword, adminStatePath);
  } else {
    console.log('⚠️  Admin credentials not set; admin.json will not be created');
  }

  console.log('\n' + '='.repeat(60));
  console.log('✅ Global Setup Complete');
  console.log(`   User: ${process.env.EMAIL}`);
  console.log('='.repeat(60) + '\n');
}

export default globalSetup;

