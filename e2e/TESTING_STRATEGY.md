# 🧪 Testing Strategy & How to Add New Tests

A concise guide to the NoteTaker test architecture and how to extend it.

---

## 📋 Testing Pyramid

```
                    ┌─────────────────┐
                    │   E2E Tests     │  ← Playwright (UI flows)
                    │   (Few, Slow)   │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │      API Fuzz Tests         │  ← Schemathesis (contract)
              │    (Automated, Nightly)     │
              └──────────────┬──────────────┘
                             │
         ┌───────────────────┴───────────────────┐
         │           Integration Tests           │  ← API + fixtures
         │        (Critical paths, Fast)         │
         └───────────────────┬───────────────────┘
                             │
    ┌────────────────────────┴────────────────────────┐
    │                  Unit Tests                      │  ← Component logic
    │              (Many, Very Fast)                   │
    └──────────────────────────────────────────────────┘
```

---

## 🎯 Test Types Summary

| Type | Tool | When to Run | Purpose |
|------|------|-------------|---------|
| **E2E UI** | Playwright | Every PR | Validate user flows |
| **API Fuzz** | Schemathesis | Nightly | Find contract violations |
| **API Integration** | Playwright + APIRequestContext | Every PR | Validate API contracts |
| **Smoke** | Playwright (`@smoke` tag) | Pre-deploy | Quick sanity check |

---

## 🚀 How to Add a New Test

### 1. E2E UI Test

```typescript
// e2e/tests/my-feature.spec.ts
import { test, expect } from '@playwright/test';
import { MyPage } from '../pages/MyPage';
import hooks from '../utils/hooks';
import pages from '../utils/pages';

test.describe('My Feature', () => {
  test('should do something', async ({ page }) => {
    // 1. Setup - use hooks for consistent navigation
    const myPage = await hooks.beforeEach(page, MyPage, pages.myFeature);
    
    // 2. Action
    await myPage.doSomething();
    
    // 3. Assert
    await expect(myPage.resultElement).toBeVisible();
  });
});
```

### 2. API Integration Test

```typescript
// e2e/tests/api/my-api.spec.ts
import { test, expect } from '@playwright/test';
import { executeRequest } from '../utils/apiRequestUtils';

test.describe('My API', () => {
  test('should create resource', async ({ request }) => {
    const response = await executeRequest(request, '/endpoint', 'post', {
      name: 'Test Item'
    });
    
    expect(response.status).toBe(201);
    expect(response.data.name).toBe('Test Item');
  });
});
```

### 3. Test with Fixtures

```typescript
// e2e/tests/my-fixture-test.spec.ts
import { test as base, expect } from '@playwright/test';
import { MyPage } from '../pages/MyPage';

// Define fixture
const test = base.extend<{ myPage: MyPage }>({
  myPage: async ({ page }, use) => {
    const myPage = new MyPage(page);
    await myPage.goto();
    await use(myPage);
  },
});

test('with fixture', async ({ myPage }) => {
  await myPage.doAction();
  await expect(myPage.result).toBeVisible();
});
```

---

## 📁 File Structure Convention

```
e2e/
├── tests/
│   ├── smoke/           # Quick sanity tests
│   ├── api/             # API-only tests
│   ├── auth/            # Authentication tests
│   └── [feature].spec.ts
├── pages/               # Page Object Models
│   └── [Feature]Page.ts
├── fixtures/            # Test fixtures
├── utils/               # Helpers
└── data/                # Test data, auth state
```

---

## ✅ Checklist for New Tests

- [ ] **Descriptive name**: `should [action] when [condition]`
- [ ] **Single responsibility**: One assertion per test (when practical)
- [ ] **Independent**: No dependencies on other tests
- [ ] **Use POM**: Page logic in `pages/`, not in tests
- [ ] **Use hooks**: `hooks.beforeEach()` for setup
- [ ] **Tag appropriately**: `@smoke`, `@regression`, `@api`
- [ ] **Handle auth**: Use `storageState` for authenticated tests

---

## 🏷️ Test Tags

```typescript
// Tag a test
test('critical flow @smoke', async ({ page }) => { ... });

// Run tagged tests
// npx playwright test --grep @smoke
// npx playwright test --grep-invert @slow
```

| Tag | Purpose | When to Run |
|-----|---------|-------------|
| `@smoke` | Critical paths only | Pre-deploy, quick validation |
| `@regression` | Full test suite | Nightly, before release |
| `@slow` | Long-running tests | Nightly only |
| `@api` | API-only tests | Every PR |
| `@flaky` | Known unstable tests | Skip in CI, fix ASAP |

---

## 🔧 Environment Configuration

Tests automatically select environment via `ENV` variable:

```bash
# Run against different environments
ENV=local npx playwright test      # Default
ENV=dev npx playwright test        # Development
ENV=prod npx playwright test       # Production (read-only tests)
```

---

## 📊 Reporting

| Report Type | Location | Purpose |
|-------------|----------|---------|
| **Playwright HTML** | `playwright-report/` | Detailed UI report |
| **Allure** | `allure-results/run-*/` | Rich interactive report |
| **CI Summary** | GitHub Actions | Quick PR feedback |

### Generate Reports Locally

```bash
# Playwright HTML
npx playwright show-report

# Allure (requires allure-cli)
npx allure generate allure-results/$(cat allure-results/.current-run) -o allure-report
npx allure open allure-report
```

---

## 🌙 Nightly Runs

Schemathesis API fuzz tests run automatically at **2:00 AM UTC** via `.github/workflows/schemathesis-nightly.yml`.

Manual trigger: **Actions → Schemathesis API Fuzz Testing (Nightly) → Run workflow**

---

## 📚 Related Documentation

- **[PLAYWRIGHT_SUMMARIZER_GUIDE.md](./scripts/PLAYWRIGHT_SUMMARIZER_GUIDE.md)** - Test report summarizer
- **[LLM_SUMMARIZER_GUIDE.md](./scripts/LLM_SUMMARIZER_GUIDE.md)** - LLM setup for summaries
- **[SCHEMATHESIS_GUIDE.md](./schemathesis/SCHEMATHESIS_GUIDE.md)** - API fuzz testing
- **[MODEL_SETUP.md](./scripts/MODEL_SETUP.md)** - LLM model configuration
