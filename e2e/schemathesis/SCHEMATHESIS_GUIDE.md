# 🔬 Schemathesis API Fuzz Testing Guide

A comprehensive guide for property-based API testing using **Schemathesis** with **Allure** reporting, integrated into the NoteTaker test automation framework.

---

## 📚 Table of Contents

- [Overview](#overview)
- [What is Schemathesis?](#what-is-schemathesis)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Configuration](#configuration)
- [Running Tests Locally](#running-tests-locally)
- [CI Integration](#ci-integration)
- [Allure Reporting](#allure-reporting)
- [Useful Commands](#useful-commands)
- [Troubleshooting](#troubleshooting)

---

## Overview

This integration provides automated API fuzz testing that:

- ✅ **Authenticates** via API to get `x-auth-token`
- ✅ **Generates test cases** from your OpenAPI specification
- ✅ **Validates responses** against the spec
- ✅ **Produces Allure reports** separate from Playwright E2E tests
- ✅ **Runs in CI** as part of the GitHub Actions workflow

---

## What is Schemathesis?

[Schemathesis](https://schemathesis.io/) is a property-based testing tool for APIs. It:

1. **Reads your OpenAPI/Swagger specification**
2. **Generates hundreds of test cases** automatically
3. **Finds edge cases** you might not think of (null values, empty strings, boundary values)
4. **Validates** that your API conforms to its specification

### What It Tests

| Check | Description |
|-------|-------------|
| `not_a_server_error` | API doesn't return 5xx errors |
| `status_code_conformance` | Response codes match spec |
| `content_type_conformance` | Content-Type headers are correct |
| `response_schema_conformance` | Response body matches schema |
| `negative_data_rejection` | Invalid data is properly rejected |
| `missing_required_header` | Required headers are enforced |

---

## Project Structure

```
NoteTaker/
├── e2e/
│   ├── schemathesis/                # 🔬 Schemathesis testing folder
│   │   ├── run_schemathesis.py      # Main test runner script
│   │   ├── requirements.txt         # Python dependencies
│   │   ├── .gitignore               # Ignore venv, results, reports
│   │   ├── SCHEMATHESIS_GUIDE.md    # This documentation
│   │   ├── venv/                    # Python virtual environment (create locally)
│   │   ├── allure-results/          # JUnit XML output (generated)
│   │   └── allure-report/           # Allure HTML report (generated)
│   │
│   ├── openapi.json                 # OpenAPI specification (used by Schemathesis)
│   ├── .env                         # Environment variables (EMAIL, PASSWORD, etc.)
│   ├── tests/                       # Playwright tests
│   └── ...                          # Other Playwright files
│
└── .github/workflows/
    └── playwright.yml               # CI workflow (includes Schemathesis)
```

---

## Setup & Installation

### Prerequisites

- **Python 3.10+** (3.12 recommended)
- **pip** (Python package manager)
- **Allure CLI** (for report generation)

### Step 1: Create Virtual Environment

```bash
# Navigate to schemathesis folder (inside e2e)
cd e2e/schemathesis

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### Step 2: Install Dependencies

```bash
# With virtual environment activated
pip install -r requirements.txt
```

### Step 3: Install Allure CLI (if not already installed)

```bash
# macOS (Homebrew)
brew install allure

# Or via npm (cross-platform)
npm install -g allure-commandline
```

### Step 4: Verify Installation

```bash
# Check Schemathesis
schemathesis --version

# Check Allure
allure --version
```

---

## Configuration

The script reads configuration from the parent `e2e/.env` file:

```env
# Required for Schemathesis
BASE_API_URL=https://practice.expandtesting.com/notes/api
EMAIL=your-email@example.com
PASSWORD=your-password

# Optional
OPENAPI_FILE=openapi.json              # Default: e2e/openapi.json
SCHEMATHESIS_MAX_EXAMPLES=50           # Max test cases per endpoint
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BASE_API_URL` | ✅ | API base URL |
| `EMAIL` | ✅ | Login email for authentication |
| `PASSWORD` | ✅ | Login password |
| `OPENAPI_FILE` | ❌ | Path to OpenAPI spec (default: `e2e/openapi.json`) |
| `SCHEMATHESIS_MAX_EXAMPLES` | ❌ | Max test cases per endpoint (default: 50) |

---

## Running Tests Locally

### Quick Start

```bash
# 1. Navigate to schemathesis folder (inside e2e)
cd e2e/schemathesis

# 2. Activate virtual environment
source venv/bin/activate

# 3. Run tests
python run_schemathesis.py
```

### Expected Output

```
======================================================================
🔬 Schemathesis API Fuzz Testing with Authentication
======================================================================
📄 Loading environment from: /path/to/e2e/.env

📋 Configuration:
   Base URL:    https://practice.expandtesting.com/notes/api
   Email:       your-email@example.com
   OpenAPI:     /path/to/e2e/openapi.json
   Results Dir: /path/to/schemathesis/allure-results

🔐 Authenticating at: https://practice.expandtesting.com/notes/api/users/login
✅ Authentication successful

🧪 Running Schemathesis...
   OpenAPI:     /path/to/e2e/openapi.json
   Base URL:    https://practice.expandtesting.com/notes/api
   Results:     /path/to/schemathesis/allure-results
   Max Examples: 50

   Command: schemathesis run ... -H x-auth-token:abc123...

======================================================================
Schemathesis v4.6.4
...
======================================================================

📁 Results in /path/to/schemathesis/allure-results:
   - junit-20251202T175208Z.xml (43,038 bytes)

======================================================================
⚠️  Schemathesis tests completed with exit code 1
   (Non-zero exit code indicates API issues were found)
======================================================================

💡 Next steps:
   Generate Allure report: allure generate allure-results -o allure-report --clean
   View Allure report:     allure open allure-report
   Or serve directly:      allure serve allure-results
```

### View Results

```bash
# Option 1: Generate and open static report
allure generate allure-results -o allure-report --clean
allure open allure-report

# Option 2: Serve directly (generates temp report)
allure serve allure-results
```

---

## CI Integration

Schemathesis runs automatically in GitHub Actions after Playwright tests.

### Workflow Steps

The CI workflow (`.github/workflows/playwright.yml`) includes:

```yaml
# ═══════════════════════════════════════════════════════════════
# 🔬 Schemathesis API Testing
# ═══════════════════════════════════════════════════════════════

- name: Setup Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.12'

- name: Install Schemathesis dependencies
  working-directory: e2e/schemathesis
  run: pip install -r requirements.txt

- name: Run Schemathesis API tests
  working-directory: e2e/schemathesis
  run: python run_schemathesis.py
  continue-on-error: true

- name: Generate Schemathesis Allure HTML report
  if: always()
  run: |
    allure generate e2e/schemathesis/allure-results --clean -o e2e/schemathesis/allure-report

- name: Upload Schemathesis Allure report artifact
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: schemathesis-allure-report
    path: e2e/schemathesis/allure-report
```

### CI Artifacts

After each CI run, you'll find **two separate artifacts**:

| Artifact | Description |
|----------|-------------|
| `allure-report` | Playwright E2E test results |
| `schemathesis-allure-report` | Schemathesis API fuzz test results |

### Downloading & Viewing CI Reports

1. Go to the GitHub Actions run
2. Scroll to **Artifacts** section
3. Download `schemathesis-allure-report`
4. Extract and view:

```bash
# Extract the downloaded zip
unzip schemathesis-allure-report.zip -d schemathesis-report

# View with Allure CLI (recommended)
allure open schemathesis-report

# Or serve with HTTP server
cd schemathesis-report
npx http-server .
# Open http://localhost:8080
```

---

## Allure Reporting

### Report Structure

The Allure report shows:

- **Overview**: Pass/fail statistics, duration
- **Suites**: Tests grouped by API endpoint
- **Categories**: Failures grouped by type
- **Timeline**: Test execution timeline
- **Behaviors**: Tests grouped by feature/story

### Generating Reports

```bash
# From schemathesis folder

# Generate static HTML report
allure generate allure-results -o allure-report --clean

# Open the report
allure open allure-report

# Or serve directly (creates temp report)
allure serve allure-results
```

### Report Screenshots

The Allure report will show:
- Each API endpoint as a test suite
- Individual test cases with request/response details
- Failure messages with reproduction commands (`curl`)

---

## Useful Commands

### Schemathesis CLI

```bash
# Run with specific checks only
schemathesis run openapi.json -u https://api.example.com \
  --checks not_a_server_error,response_schema_conformance

# Run specific endpoints only
schemathesis run openapi.json -u https://api.example.com \
  --include-path "/users/*"

# Exclude endpoints
schemathesis run openapi.json -u https://api.example.com \
  --exclude-path "/health-check"

# Limit test cases per endpoint
schemathesis run openapi.json -u https://api.example.com \
  -n 20

# Run with authentication header
schemathesis run openapi.json -u https://api.example.com \
  -H "x-auth-token:your-token-here"

# Generate JUnit report
schemathesis run openapi.json -u https://api.example.com \
  --report junit --report-dir ./results

# Dry run (validate spec without testing)
schemathesis run openapi.json -u https://api.example.com \
  --dry-run
```

### Virtual Environment

```bash
# Create
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Deactivate
deactivate

# Install dependencies
pip install -r requirements.txt

# Update dependencies
pip install --upgrade schemathesis requests
pip freeze > requirements.txt
```

### Allure CLI

```bash
# Generate report
allure generate allure-results -o allure-report --clean

# Open report (starts local server)
allure open allure-report

# Serve directly from results
allure serve allure-results

# Serve on specific port
allure serve allure-results --port 9999
```

---

## Troubleshooting

### Common Issues

#### 1. "schemathesis: command not found"

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Verify installation
pip show schemathesis
```

#### 2. "No authentication token specified"

The script authenticates automatically. If you see auth errors:

```bash
# Check your e2e/.env file has correct credentials
cat ../e2e/.env | grep -E "EMAIL|PASSWORD|BASE_API_URL"
```

#### 3. "OpenAPI file not found"

```bash
# Verify the file exists
ls -la ../e2e/openapi.json

# Or specify a custom path
OPENAPI_FILE=/path/to/your/openapi.json python run_schemathesis.py
```

#### 4. Allure report shows empty/no tests

```bash
# Check that JUnit XML was generated
ls -la allure-results/

# Regenerate report
allure generate allure-results -o allure-report --clean
```

#### 5. SSL/Certificate errors

```bash
# Add to your command or script
schemathesis run openapi.json -u https://api.example.com \
  --tls-verify false
```

### Debug Mode

For verbose output, modify the script or run Schemathesis directly:

```bash
# Activate venv
source venv/bin/activate

# Get auth token manually
curl -X POST https://practice.expandtesting.com/notes/api/users/login \
  -d "email=your@email.com&password=yourpassword"

# Run Schemathesis with token
schemathesis run ../e2e/openapi.json \
  -u https://practice.expandtesting.com/notes/api \
  -H "x-auth-token:YOUR_TOKEN_HERE" \
  --checks all \
  -n 10
```

---

## Integration with Playwright

This Schemathesis setup is designed to complement Playwright E2E tests:

| Aspect | Playwright | Schemathesis |
|--------|------------|--------------|
| **Focus** | UI/E2E flows | API contract & edge cases |
| **Test Generation** | Manual | Automatic from OpenAPI |
| **Authentication** | Browser cookies | API token header |
| **Report** | `allure-report` | `schemathesis-allure-report` |
| **Language** | TypeScript | Python |

Both run in CI and produce separate Allure reports for comprehensive coverage.

---

## Resources

- [Schemathesis Documentation](https://schemathesis.readthedocs.io/)
- [Schemathesis GitHub](https://github.com/schemathesis/schemathesis)
- [Allure Framework](https://allurereport.org/)
- [OpenAPI Specification](https://swagger.io/specification/)

---

**Built with ❤️ for comprehensive API testing**
