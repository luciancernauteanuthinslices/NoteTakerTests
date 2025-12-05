# 🗒️ NoteTaker E2E Test Automation Framework

A **production-ready** Playwright test automation framework with multi-environment support, multi-role authentication, Page Object Model, API integration, and comprehensive test fixtures.

[![Playwright](https://img.shields.io/badge/Playwright-2EAD33?style=for-the-badge&logo=playwright&logoColor=white)](https://playwright.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Node.js](https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)](https://nodejs.org/)

</div>

---

## 📚 Table of Contents

- [🔗 Quick Links](#-quick-links)
- [⚡ Quick Start](#-quick-start)
- [📁 Project Structure](#-project-structure)
- [⚙️ Configuration](#️-configuration)
- [🌍 Multi-Environment Setup](#-multi-environment-setup)
- [👥 Multi-Role Authentication](#-multi-role-authentication)
- [🔐 Authentication Methods](#-authentication-methods)
- [📄 Page Object Model](#-page-object-model)
- [🧪 Fixtures](#-fixtures)
- [🌐 API Testing](#-api-testing)
- [📝 Writing Tests](#-writing-tests)
- [🚀 Running Tests](#-running-tests)
- [📊 Reporting](#-reporting)
- [🔬 Schemathesis API Fuzz Testing](#-schemathesis-api-fuzz-testing)
- [🤖 LLM Test Report Summarizer](#-llm-test-report-summarizer)

---

## 🔗 Quick Links

| Resource | Link |
|----------|------|
| 🌐 **Application Under Test** | [NoteTaker App](https://practice.expandtesting.com/notes/app) |
| 📖 **API Documentation (Swagger)** | [API Docs](https://practice.expandtesting.com/notes/api/api-docs/) |
| 🎭 **Playwright Documentation** | [playwright.dev](https://playwright.dev/docs/intro) |
| 📚 **Playwright API Reference** | [API Reference](https://playwright.dev/docs/api/class-playwright) |

---

## ⚡ Quick Start

```bash
# 1. Navigate to e2e directory
cd e2e

# 2. Install dependencies
npm install

# 3. Install Playwright browsers
npx playwright install

# 4. Create your environment file
cp .env.example .env

# 5. Run tests
npx playwright test
```

---

## 📁 Project Structure

```
e2e/
├── 📁 data/                          # Test data & authentication storage
│   ├── 📁 auth/                      # Multi-role auth storage states
│   │   ├── admin.json                # Admin user session storage
│   │   └── user.json                 # Normal user session storage
│   ├── storageState.json             # Single user storage state (globalSetup)
│   └── userData.ts                   # Static test data (invalid credentials, etc.)
│
├── 📁 tests/                         # Test specifications
│   ├── 📁 setup/                     # Authentication setup files
│   │   ├── globalSetup.ts            # Single-user global auth (runs once)
│   │   └── authSetup.ts              # Multi-role auth setup (admin + user)
│   │
│   ├── 📁 multi-role-specs/          # Tests requiring specific roles
│   │   ├── profile-stored-auth-multi-role-login-admin.spec.ts
│   │   └── profile-stored-auth-multi-role-login-user.spec.ts
│   │
│   ├── login.spec.ts                 # Login functionality tests
│   ├── note-with-fixture-and-api.spec.ts  # API-based tests with fixtures
│   ├── profile-with-dynamic-pom.spec.ts   # Dynamic POM tests
│   └── profile-with-fixtures.spec.ts      # Fixture-based tests
│
├── 📁 ui/                            # UI automation infrastructure
│   ├── 📁 api/                       # API layer
│   │   └── 📁 requests/              # API request functions
│   │       └── notes-api.ts          # Notes & Auth API methods
│   │
│   ├── 📁 fixtures/                  # Playwright fixtures
│   │   ├── notes-fixtures.ts         # Page setup fixtures
│   │   └── login-with-api-token-fixture.ts  # API auth fixture
│   │
│   ├── 📁 pages/                     # Page Object Models
│   │   ├── homePage.ts               # Home/Notes page POM
│   │   ├── loginPage.ts              # Login page POM
│   │   ├── profilePage.ts            # Profile page POM
│   │   └── registrationPage.ts       # Registration page POM
│   │
│   └── 📁 utils/                     # Utility functions
│       ├── apiEndpoints.ts           # API endpoint definitions
│       ├── apiRequestUtils.ts        # Generic API request helper
│       ├── hooks.ts                  # Test lifecycle hooks
│       ├── messages.ts               # UI message constants
│       ├── pages.ts                  # Page URL paths (with app prefix)
│       ├── uiPages.ts                # Page URL paths (without prefix)
│       └── uiUrlBuilder.ts           # URL builder with params
│
├── 📁 scripts/                       # 🤖 LLM & utility scripts
│   ├── run_llm_once.py               # Simple LLM test script
│   ├── summarize_playwright_results.py    # Playwright report summarizer
│   ├── summarize_schemathesis_results.py  # Schemathesis report summarizer
│   ├── PLAYWRIGHT_SUMMARIZER_GUIDE.md     # Playwright summarizer docs
│   ├── LLM_SUMMARIZER_GUIDE.md            # LLM setup documentation
│   └── MODEL_SETUP.md                     # LLM model configuration guide
│
├── 📁 schemathesis/                  # 🔬 API fuzz testing
│   ├── run_schemathesis.py           # Schemathesis runner
│   ├── requirements.txt              # Python dependencies
│   ├── Dockerfile                    # Docker image for Schemathesis
│   ├── docker-compose.yml            # Docker Compose config
│   ├── venv/                         # Python virtual environment
│   ├── allure-results/               # Schemathesis results (timestamped)
│   │   ├── .current-run              # Current run ID marker
│   │   └── run-YYYYMMDD-HHMMSS/      # Timestamped run folders
│   └── SCHEMATHESIS_GUIDE.md         # Schemathesis documentation
│
├── TESTING_STRATEGY.md               # 🧪 Testing strategy & how to add tests
│
├── 📁 extensions/                    # Browser extensions (e.g., ad blocker)
├── 📁 allure-results/                # Playwright results (timestamped)
│   ├── .current-run                  # Current run ID marker
│   └── run-YYYYMMDD-HHMMSS/          # Timestamped run folders
├── 📁 playwright-report/             # HTML report output
├── 📁 test-results/                  # Test artifacts (screenshots, traces)
│
├── .env                              # Local environment variables
├── .env.dev                          # Development environment
├── .env.prod                         # Production environment
├── playwright.config.ts              # Playwright configuration
└── package.json                      # Dependencies & scripts
```

---

## ⚙️ Configuration

### `playwright.config.ts`

The configuration file controls all test execution settings:

```typescript
import { defineConfig, devices } from '@playwright/test';
import dotenv from 'dotenv';
import path from 'path';

// Dynamic environment selection
const envName = process.env.ENV ?? 'local';
const envFile = envName === 'prod' ? '.env.prod' 
             : envName === 'dev' ? '.env.dev' 
             : '.env';

dotenv.config({ path: path.resolve(__dirname, envFile) });

export default defineConfig({
  // 🔐 Global Setup - Single user authentication
  globalSetup: require.resolve('./tests/setup/globalSetup'),
  
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  
  reporter: [['html'], ['allure-playwright']],
  
  use: {
    // 🔑 Storage state for authenticated sessions
    storageState: 'data/storageState.json',
    baseURL: process.env.APP_URL!,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    headless: false,
  },

  projects: [
    // ✅ Active: Single user with globalSetup
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    // 🔄 Alternative: UI-based multi-role auth
    // {
    //   name: 'auth-setup',
    //   testMatch: /authSetup\.ts/,
    // },
    // {
    //   name: 'chromium-auth',
    //   use: { ...devices['Desktop Chrome'] },
    //   dependencies: ['auth-setup'],
    // },
  ],
});
```

### Key Configuration Options

| Option | Description |
|--------|-------------|
| `globalSetup` | Runs authentication once before all tests |
| `storageState` | Path to saved browser session (cookies, localStorage) |
| `baseURL` | Application base URL from environment |
| `fullyParallel` | Run tests in parallel across files |
| `retries` | Number of retry attempts for failed tests |

---

## 🌍 Multi-Environment Setup

The framework supports multiple environments through `.env` files:

### Environment Files

| File | Environment | Usage |
|------|-------------|-------|
| `.env` | Local/Default | `npm test` |
| `.env.dev` | Development | `ENV=dev npm test` |
| `.env.prod` | Production | `ENV=prod npm test` |

### Environment Variables Template

Create your `.env` file with these variables:

```env
# ═══════════════════════════════════════════════════════════
# 🔗 APPLICATION URLS
# ═══════════════════════════════════════════════════════════
APP_URL=https://practice.expandtesting.com/notes/
BASE_API_URL=https://practice.expandtesting.com/notes/api

# ═══════════════════════════════════════════════════════════
# 👤 SINGLE USER CREDENTIALS (for globalSetup)
# ═══════════════════════════════════════════════════════════
EMAIL=your-email@example.com
PASSWORD=your-password
# These can be static test credentials managed outside the test run
# (see "Authentication Methods" – Method 1, static user variant).

# ═══════════════════════════════════════════════════════════
# 👥 MULTI-ROLE CREDENTIALS (for authSetup)
# ═══════════════════════════════════════════════════════════
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin-password
```

### Running with Different Environments

```bash
# Local environment (default)
npx playwright test

# Development environment
ENV=dev npx playwright test

# Production environment
ENV=prod npx playwright test
```

---

## 👥 Multi-Role Authentication

The framework supports testing with multiple user roles (admin, normal user).

### Storage Files

```
e2e/data/auth/
├── admin.json    # Admin session state
└── user.json     # Normal user session storage
```

### Auth Setup (`tests/setup/authSetup.ts`)

```typescript
import { test as setup } from '@playwright/test';
import { LoginPage } from '../../ui/pages/loginPage';

const authDir = 'data/auth';
const adminFile = `${authDir}/admin.json`;
const userFile = `${authDir}/user.json`;

// Parallel login for both roles
setup.describe.configure({ mode: 'parallel' });

setup('Authenticate as admin', { tag: '@multirole' }, async ({ page }) => {
  const email = process.env.ADMIN_EMAIL!;
  const password = process.env.ADMIN_PASSWORD!;
  await doLogin(page, email, password);
  await page.context().storageState({ path: adminFile });
});

setup('Authenticate as user', { tag: '@multirole' }, async ({ page }) => {
  const email = process.env.EMAIL!;
  const password = process.env.PASSWORD!;
  await doLogin(page, email, password);
  await page.context().storageState({ path: userFile });
});
```

### Using Multi-Role in Tests

```typescript
// Admin-specific test
test.use({ storageState: 'data/auth/admin.json' });

test('Admin can access dashboard', async ({ page }) => {
  // Test runs as admin
});
```

```typescript
// Normal user test
test.use({ storageState: 'data/auth/user.json' });

test('User can view profile', async ({ page }) => {
  // Test runs as normal user
});
```

### Enabling Multi-Role in Config

Uncomment the auth-setup project in `playwright.config.ts`:

```typescript
projects: [
  // Enable this for multi-role auth
  {
    name: 'auth-setup',
    testMatch: /authSetup\.ts/,
  },
  {
    name: 'chromium-auth',
    use: { ...devices['Desktop Chrome'] },
    dependencies: ['auth-setup'],
  },
]
```

---

## 🔐 Authentication Methods

### Method 1: Global Setup (Single User) ✅ **Default**

- **File:** `tests/setup/globalSetup.ts`
- **Storage:** `data/storageState.json`
- **Best for:** Most test scenarios with single user
- **Behavior:** Registers a fresh user via the UI on each test run and updates the active env file (`.env`, `.env.dev` or `.env.prod`, depending on `ENV`) with the new `EMAIL` / `PASSWORD` values.

```typescript
// playwright.config.ts
export default defineConfig({
  globalSetup: require.resolve('./tests/setup/globalSetup'),
  use: {
    storageState: 'data/storageState.json',
  },
});
```

When Playwright starts, `globalSetup` will:

- Generate random registration data via `data/userGenerator.ts`.
- Open the registration page and create a new account using `RegistrationPage`.
- Persist the new credentials into the active env file (`.env`, `.env.dev` or `.env.prod`), preserving other environment variables.
- Log in once with this user and save `data/storageState.json`.
- Copy that state to `data/auth/user.json` and `data/auth/admin.json` (or reuse the same state if dedicated admin credentials are not provided).

This ensures that every test run uses a clean user account and avoids data pollution between runs.

#### Login strategy options in `globalSetup.ts`

There are two ways to log in and create `data/storageState.json`. You control them by commenting/uncommenting blocks in `tests/setup/globalSetup.ts`:

- **Option A – Login each run with new user using Faker (default)**

```typescript
// Login each run with new user using Faker

// Generate new user with Faker
const newUser = generateRegistrationData();
  
console.log(`Generated user: ${newUser.email}`);
  
// Register the new user
await registerNewUser(baseURL as string, newUser);
  
// Update env file with new credentials
updateEnvFile(newUser.email, newUser.password);
  
// Login and save storage state
await loginAndSaveState(
  baseURL as string,
  newUser.email,
  newUser.password,
  storageState as string
);
```

Leave this block active (and keep the static user block commented) when you want a fresh, unique user for every test run.

- **Option B – Login with static user from environment**

```typescript
// Login with static user from environment
console.log(`Logging in with static user: ${process.env.EMAIL}`);
  
await loginAndSaveState(
  baseURL as string,
  process.env.EMAIL as string,
  process.env.PASSWORD as string,
  storageState as string
);
```

To use this option instead of auto-registration:

- Comment out or remove the Option A block above.
- Uncomment the static user block.
- Ensure `EMAIL` and `PASSWORD` are set in the correct env file (`.env`, `.env.dev`, `.env.prod`).

#### Variant: Static Test User (No Per-Run Registration)

If you prefer to use a static test account instead of registering a new user on each run:

- Create a dedicated test user in the application (for example, `testuser@example.com`).
- Set `EMAIL` and `PASSWORD` in `e2e/.env` to that user's credentials (see the *Multi-Environment Setup* section).
- Configure your `globalSetup` implementation to skip the registration step and only log in with these credentials to produce `data/storageState.json`.
 Remove / skip:
 ```typescript
// Register the new user
  await registerNewUser(baseURL as string, newUser);
  
  // Update .env with new credentials
  updateEnvFile(newUser.email, newUser.password);
  ```
Instead, call 
loginAndSaveState
 with process.env.EMAIL and process.env.PASSWORD to create storageState from those static credentials.

This approach is useful when user creation is handled by a separate seeding job or when you want fully deterministic credentials across runs.

### Method 2: Auth Setup Project (Multi-Role)

- **File:** `tests/setup/authSetup.ts`
- **Storage:** `data/auth/admin.json`, `data/auth/user.json`
- **Best for:** Role-based access testing

```typescript
// playwright.config.ts - Uncomment to enable
projects: [
  {
    name: 'auth-setup',
    testMatch: /authSetup\.ts/,
  },
  {
    name: 'chromium-auth',
    use: { ...devices['Desktop Chrome'] },
    dependencies: ['auth-setup'],
  },
]
```

### Method 3: API Token Fixture

- **File:** `ui/fixtures/login-with-api-token-fixture.ts`
- **Best for:** API-only tests, faster execution

```typescript
import { test } from '../ui/fixtures/login-with-api-token-fixture';

test('API test with auth token', async ({ apiContext }) => {
  const response = await apiContext.get('/notes');
  expect(response.ok()).toBeTruthy();
});
```

---

## 📄 Page Object Model

### Structure

Each page has a dedicated class with:
- **Locators:** Element selectors as class properties
- **Actions:** Methods for user interactions
- **Assertions:** Methods to verify page state

### Example: `LoginPage`

```typescript
export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly loginButton: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.locator('#email');
    this.passwordInput = page.locator('#password');
    this.loginButton = page.getByRole('button', { name: 'Login' });
  }

  async doLogin(email: string, password: string): Promise<void> {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.loginButton.click();
  }

  async checkLoggedIn(): Promise<boolean> {
    return await this.homePageTitle.innerText() === '  MyNotes';
  }
}
```

### Available Page Objects

| Page Object | File | Description |
|------------|------|-------------|
| `LoginPage` | `ui/pages/loginPage.ts` | Login form interactions |
| `HomePage` | `ui/pages/homePage.ts` | Notes list, CRUD operations |
| `ProfilePage` | `ui/pages/profilePage.ts` | User profile management |
| `RegistrationPage` | `ui/pages/registrationPage.ts` | New user registration |

### Dynamic POM Initialization

Use the `hooks.beforeEach()` helper for dynamic page initialization:

```typescript
import hooks from '../ui/utils/hooks';
import { ProfilePage } from '../ui/pages/profilePage';
import pages from '../ui/utils/pages';

let profilePage: ProfilePage;

test.beforeEach(async ({ page }) => {
  profilePage = await hooks.beforeEach(page, ProfilePage, pages.profile);
});
```

---

## 🧪 Fixtures

Fixtures provide reusable test setup and teardown logic.

### Notes Fixture (`ui/fixtures/notes-fixtures.ts`)

Provides a pre-configured `HomePage` with automatic note cleanup:

```typescript
import { test } from '../ui/fixtures/notes-fixtures';

test('Create note with clean slate', async ({ homePage }) => {
  // homePage is initialized and all existing notes are deleted
  await homePage.fillNote('Work', 'Meeting Notes', 'Discuss project timeline');
});
```

### API Authentication Fixture (`ui/fixtures/login-with-api-token-fixture.ts`)

Provides an authenticated API context for API testing:

```typescript
import { test, expect } from '../ui/fixtures/login-with-api-token-fixture';
import notesApi from '../ui/api/requests/notes-api';

test('Create and delete note via API', async ({ apiContext }) => {
  // apiContext is already authenticated with x-auth-token header
  const response = await notesApi.createNote(apiContext, 'Title', 'Desc', 'Work');
  expect(response.success).toBe(true);
});
```

---

## 🌐 API Testing

### API Structure

```
ui/api/
└── requests/
    └── notes-api.ts    # All API functions
```

### Available API Functions

| Function | Method | Endpoint | Description |
|----------|--------|----------|-------------|
| `login()` | POST | `/users/login` | Authenticate and get token |
| `createNote()` | POST | `/notes` | Create new note |
| `getAllNotes()` | GET | `/notes` | Get all user notes |
| `deleteNoteById()` | DELETE | `/notes/{id}` | Delete specific note |
| `getUserProfile()` | GET | `/users/profile` | Get user profile |

### API Endpoints (`ui/utils/apiEndpoints.ts`)

```typescript
export default {
  account: {
    login: '/users/login',
    logout: '/users/logout',
    profile: '/users/profile',
  },
  notes: {
    getNotes: '/notes',
    postNote: '/notes',
    deleteNote: '/notes/',   // + noteId
    updateNote: '/notes/',   // + noteId
  }
}
```

### Example API Test

```typescript
import { test, expect } from '../ui/fixtures/login-with-api-token-fixture';
import notesApi, { NoteData } from '../ui/api/requests/notes-api';

test.describe('Notes API Tests', () => {
  let createdNote: NoteData;

  test('Create, verify, and delete note', async ({ apiContext }) => {
    // Create
    const createResponse = await notesApi.createNote(
      apiContext, 'Test Note', 'Description', 'Work'
    );
    expect(createResponse.success).toBe(true);
    createdNote = createResponse.data;

    // Verify
    expect(createdNote.id).toBeTruthy();
    expect(createdNote.title).toBe('Test Note');

    // Delete
    const deleteResponse = await notesApi.deleteNoteById(apiContext, createdNote.id);
    expect(deleteResponse.success).toBe(true);
  });
});
```

---

## 📝 Writing Tests

### Basic Test Structure

```typescript
import { test, expect } from '@playwright/test';
import { HomePage } from '../ui/pages/homePage';
import hooks from '../ui/utils/hooks';
import pages from '../ui/utils/pages';

let homePage: HomePage;

test.beforeEach(async ({ page }) => {
  homePage = await hooks.beforeEach(page, HomePage, pages.homePage);
});

test.describe('Notes Management', () => {
  test('User can create a new note', async () => {
    await homePage.fillNote('Personal', 'My Note', 'Note description');
    expect(await homePage.getCardTitle()).toContain('My Note');
  });
});
```

### Test with Fresh Session (No Auth)

```typescript
test.use({ storageState: { cookies: [], origins: [] } });

test.describe('Login Tests', () => {
  test('Valid login credentials', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.doLogin(email, password);
    await loginPage.checkLoggedIn();
  });
});
```

### Test with Specific Role

```typescript
test.use({ storageState: 'data/auth/admin.json' });

test.describe('Admin Features', () => {
  test('Admin dashboard access', async ({ page }) => {
    // Test runs with admin session
  });
});
```

### Serial Test Execution

```typescript
test.describe.configure({ mode: 'serial' });

test.describe('Dependent Tests', () => {
  test('Step 1: Create data', async () => { });
  test('Step 2: Verify data', async () => { });
  test('Step 3: Cleanup', async () => { });
});
```

---

## 🚀 Running Tests

### Common Commands

```bash
# Run all tests
npx playwright test

# Run specific test file
npx playwright test tests/login.spec.ts

# Run tests with specific tag
npx playwright test --grep @multirole

# Run in headed mode
npx playwright test --headed

# Run specific project
npx playwright test --project=chromium

# Run with UI mode (interactive)
npx playwright test --ui

# Debug mode
npx playwright test --debug
```

### NPM Scripts

```bash
# Run auth setup for admin
npm run test-auth-admin

# Run auth setup for user
npm run test-auth-user
```

### Environment-Specific Runs

```bash
# Run against development
ENV=dev npx playwright test

# Run against production
ENV=prod npx playwright test
```

---

## 📊 Reporting

### HTML Report

```bash
# Run tests and generate report
npx playwright test

# Open HTML report
npx playwright show-report
```

### Allure Report

Test results are organized in **timestamped folders** for better history tracking:

```
allure-results/
├── .current-run                    # Points to latest run
├── run-20251203-143022/            # Run from Dec 3, 2:30 PM
│   ├── *-result.json               # Test results
│   └── *-attachment.*              # Screenshots, etc.
├── run-20251203-150815/            # Run from Dec 3, 3:08 PM
└── run-20251203-175645/            # Latest run
```

```bash
# Generate Allure report from latest run
LATEST_RUN=$(cat allure-results/.current-run)
npx allure generate "allure-results/$LATEST_RUN" --clean -o allure-report

# Or generate from all results
npx allure generate allure-results --clean

# Open Allure report
npx allure open
```

The summarizer scripts automatically detect the latest run folder.

### Test Artifacts

On failure, the framework captures:
- 📸 **Screenshots:** `test-results/`
- 🔍 **Traces:** Viewable via `npx playwright show-trace`
- 📹 **Videos:** (if enabled in config)

---

## 🛠️ Utilities Reference

### `hooks.ts` - Test Lifecycle Hooks

```typescript
// Navigate to page and initialize POM
const profilePage = await hooks.beforeEach(page, ProfilePage, pages.profile);
```

### `uiUrlBuilder.ts` - URL Builder with Query Params

```typescript
import { buildUrl } from './uiUrlBuilder';

// /profile?tab=settings
const url = buildUrl('profile', { tab: 'settings' });
```

### `messages.ts` - UI Message Constants

```typescript
import messages from './messages';

// Use in assertions
expect(errorText).toBe(messages.login.invalid);
```

### `apiRequestUtils.ts` - Generic API Helper

```typescript
import { executeRequest } from './apiRequestUtils';

const response = await executeRequest(apiContext, '/endpoint', 'post', { data });
```

---

## 🔧 Folder Functionality Summary

| Folder | Purpose | Key Files |
|--------|---------|-----------|
| `data/` | Test data & session storage | `storageState.json`, `userData.ts` |
| `data/auth/` | Multi-role session files | `admin.json`, `user.json` |
| `tests/setup/` | Authentication setup | `globalSetup.ts`, `authSetup.ts` |
| `tests/multi-role-specs/` | Role-specific tests | Admin/User test files |
| `ui/pages/` | Page Object Models | `loginPage.ts`, `homePage.ts`, etc. |
| `ui/fixtures/` | Reusable test fixtures | `notes-fixtures.ts` |
| `ui/api/requests/` | API request functions | `notes-api.ts` |
| `ui/utils/` | Helper utilities | Endpoints, hooks, messages |

---

## 🔬 Schemathesis API Fuzz Testing

This project includes **Schemathesis** for automated property-based API testing. Schemathesis generates test cases from your OpenAPI specification and validates that your API conforms to its contract.

### Features

- ✅ **Automatic test generation** from OpenAPI spec
- ✅ **Authentication** via API token (`x-auth-token`)
- ✅ **Allure reporting** (separate from Playwright reports)
- ✅ **CI integration** with GitHub Actions

### Quick Start

```bash
# Navigate to schemathesis folder (inside e2e)
cd e2e/schemathesis

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run tests
python run_schemathesis.py

# View Allure report
allure serve allure-results
```

Schemathesis reuses the same `e2e/.env` configuration used by Playwright.
Make sure at least the following variables are set before running `run_schemathesis.py`:

- `BASE_API_URL` – API base URL (for example, `https://practice.expandtesting.com/notes/api`).
- `EMAIL` / `PASSWORD` – credentials for obtaining the `x-auth-token` used in API requests.

For advanced configuration options and troubleshooting, see the dedicated **Schemathesis Guide** linked below.

### CI Reports

In GitHub Actions, Schemathesis produces a separate artifact:

| Artifact | Description |
|----------|-------------|
| `allure-report` | Playwright E2E test results |
| `schemathesis-allure-report` | Schemathesis API fuzz test results |
| `schemathesis-nightly-report` | Nightly fuzz test results (extended) |

### 🌙 Nightly Runs

Schemathesis runs extended API fuzz tests nightly at **2:00 AM UTC** via `.github/workflows/schemathesis-nightly.yml`.

- **More examples per endpoint** (100 vs 50 in regular CI)
- **Manual trigger available** in GitHub Actions
- **Separate artifact** for detailed analysis

### 🐳 Docker Support

```bash
cd e2e/schemathesis

# Run with Docker Compose
docker-compose up --build

# Or run with Docker directly
docker build -t schemathesis-runner .
docker run --env-file ../.env schemathesis-runner
```

### 📖 Full Documentation

For complete setup instructions, configuration options, and troubleshooting, see:

**[📚 Schemathesis Guide](./e2e/schemathesis/SCHEMATHESIS_GUIDE.md)**

---

## 🤖 LLM Test Report Summarizers

This project includes **LLM-powered summarizers** that generate intelligent recommendations from test results using a local language model.

### Available Summarizers

| Summarizer | Input | Output |
|------------|-------|--------|
| **Playwright Summarizer** | Allure JSON (`e2e/allure-results`) | E2E test summary with pass/fail/skip stats |
| **Schemathesis Summarizer** | JUnit XML (`e2e/schemathesis/allure-results`) | API fuzz test summary with HTTP recommendations |

### Features

- ✅ **Local LLM execution** using llama-cpp-python (no API keys needed)
- ✅ **Configurable model path** via `LLM_MODEL_PATH` environment variable
- ✅ **Parses Allure JSON & JUnit XML** from test frameworks
- ✅ **Deterministic fallback** when LLM is unavailable
- ✅ **CI integration** with GitHub Actions job summary
- ✅ **Rich output** with status icons (✅ ❌ ⏭️ 💔), tables, and recommendations
- ⚠️ **Hallucination disclaimer** - small 0.5B model may produce imprecise advice

### Quick Start

```bash
# Navigate to schemathesis folder (has the venv with dependencies)
cd e2e/schemathesis

# Activate virtual environment
source venv/bin/activate  # macOS/Linux

# Install llama-cpp-python (if not already installed)
pip install llama-cpp-python

# Run Playwright summarizer
python ../scripts/summarize_playwright_results.py

# Run Schemathesis summarizer
python ../scripts/summarize_schemathesis_results.py

# CI mode (clean markdown, no LLM)
python ../scripts/summarize_playwright_results.py --ci
python ../scripts/summarize_schemathesis_results.py --ci
```

### Model Setup

Download the **Qwen2.5-0.5B-Instruct** model (~400MB) from Hugging Face:

```bash
# Download the GGUF model
curl -L -o ~/Models/Qwen2.5-0.5B-Instruct-Q4_0.gguf \
  "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_0.gguf"

# Set environment variable (add to .bashrc/.zshrc for persistence)
export LLM_MODEL_PATH=~/Models/Qwen2.5-0.5B-Instruct-Q4_0.gguf
```

For detailed setup instructions, see **[MODEL_SETUP.md](./e2e/scripts/MODEL_SETUP.md)**.

### CI Reports

In GitHub Actions, both summarizers output to the job summary:

```markdown
## 🎭 Playwright E2E Test Summary
| Status | Count | Percentage |
| ✅ Passed | 9 | 100% |
...

---

## 🔬 Schemathesis API Test Summary
| Category | Count |
| Missing Allow header | 55 |
...
```

### 📖 Full Documentation

| Guide | Description |
|-------|-------------|
| **[🧪 Testing Strategy](./e2e/TESTING_STRATEGY.md)** | Testing pyramid, how to add new tests |
| **[📚 Playwright Summarizer Guide](./e2e/scripts/PLAYWRIGHT_SUMMARIZER_GUIDE.md)** | Playwright E2E test report summarizer |
| **[📚 Schemathesis Summarizer Guide](./e2e/scripts/LLM_SUMMARIZER_GUIDE.md)** | Schemathesis API test summarizer |
| **[🤖 Model Setup Guide](./e2e/scripts/MODEL_SETUP.md)** | LLM model configuration & download |

---

**Built with ❤️ using [Playwright](https://playwright.dev), [Schemathesis](https://schemathesis.io), and [llama-cpp-python](https://github.com/abetlen/llama-cpp-python)**

</div>
