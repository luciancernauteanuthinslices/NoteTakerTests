# 🎭 Playwright Test Report Summarizer Guide

A comprehensive guide for generating intelligent Playwright E2E test summaries using **llama-cpp-python** for AI-powered insights.

---

## 📚 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [How It Works](#how-it-works)
- [Setup & Installation](#setup--installation)
- [Usage](#usage)
- [Understanding the Output](#understanding-the-output)
- [Fine-Tuning LLM Parameters](#fine-tuning-llm-parameters)
- [Prompt Engineering](#prompt-engineering)
- [CI Integration](#ci-integration)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)

---

## Overview

This script parses **Allure JSON results** from Playwright test runs and generates:

- ✅ **Detailed statistics** (passed, failed, skipped, broken)
- ✅ **Performance metrics** (duration, averages)
- ✅ **Failure analysis** with error messages
- ✅ **Suite breakdowns** for multi-suite projects
- ✅ **Actionable recommendations** based on results
- ✅ **AI-powered insights** using a local LLM (optional)

> **Note:** Environment info and slowest tests are available in the full Allure HTML report.

---

## Features

| Feature | Description |
|---------|-------------|
| 📊 **Statistics Table** | Pass/fail/skip counts with percentages |
| ⏱️ **Performance Metrics** | Total and average test duration |
| ❌ **Failure Details** | Test names, files, and error messages |
| 📦 **Suite Breakdown** | Results grouped by test suite |
| 💡 **Recommendations** | Rule-based actionable suggestions |
| 🤖 **AI Insights** | LLM-generated analysis (optional) |

### Status Icons

| Icon | Status | Description |
|------|--------|-------------|
| ✅ | Passed | Test completed successfully |
| ❌ | Failed | Test assertion failed |
| 💔 | Broken | Test crashed or had setup issues |
| ⏭️ | Skipped | Test was intentionally skipped |

---

## How It Works

```
┌─────────────────────┐
│  Allure JSON Files  │
│  (*-result.json)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Parse & Extract    │
│  - Test names       │
│  - Status           │
│  - Duration         │
│  - Errors           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Aggregate Stats    │
│  - Counts           │
│  - Pass rate        │
│  - Suite breakdown  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Generate Report    │
│  - Deterministic    │
│  - LLM insights     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Markdown Output    │
│  (stdout/summary)   │
└─────────────────────┘
```

### Data Flow

1. **Find Latest Run**: Check `.current-run` marker or find newest `run-*` folder
2. **Find Files**: Locate all `*-result.json` files in the results directory
3. **Parse JSON**: Extract test name, status, duration, steps, and errors
4. **Aggregate**: Calculate statistics and group by suite
5. **Generate**: Create markdown with tables, lists, and recommendations
6. **Output**: Print to stdout (for CI) or decorated console (for local)

### Timestamped Results Organization

Results are organized in timestamped folders for history tracking:

```
allure-results/
├── .current-run                    # Contains: "run-20251203-175645"
├── run-20251203-143022/            # Older run
│   ├── abc123-result.json
│   └── def456-attachment.txt
├── run-20251203-150815/            # Another run
└── run-20251203-175645/            # Latest run (matches .current-run)
    ├── *-result.json
    └── *-attachment.*
```

The script automatically detects the latest run by:
1. Reading `.current-run` marker file (written by test runner)
2. Falling back to the newest `run-*` folder by timestamp sorting
3. Supporting legacy flat structure if no run folders exist

---

## Setup & Installation

### Prerequisites

- **Python 3.10+**
- **Playwright** with Allure reporter configured
- **llama-cpp-python** (optional, for AI insights)

### Step 1: Ensure Playwright Produces Allure Results

In your `playwright.config.ts`:

```typescript
export default defineConfig({
  reporter: [
    ['html'],
    ['allure-playwright']  // This generates the JSON files
  ],
  // ...
});
```

### Step 2: Use the Existing Virtual Environment

```bash
# Navigate to schemathesis folder (has the venv)
cd e2e/schemathesis

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
```

### Step 3: Install llama-cpp-python (Optional)

Only needed if you want AI insights:

```bash
pip install llama-cpp-python

# For macOS with Metal GPU:
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python --force-reinstall
```

### Step 4: Verify Installation

```bash
# Test the script
python ../scripts/summarize_playwright_results.py --help
```

---

## Usage

### Basic Usage

```bash
# Activate venv
cd e2e/schemathesis
source venv/bin/activate

# Run summarizer (uses default path: ../allure-results)
python ../scripts/summarize_playwright_results.py

# Specify custom path
python ../scripts/summarize_playwright_results.py --results ../allure-results
```

### Command Line Options

| Option | Description |
|--------|-------------|
| `--ci` | CI mode: clean markdown, no LLM, no progress messages |
| `--results PATH` | Path to allure-results directory |
| `--no-llm` | Skip LLM insights (deterministic only) |
| `--compact` | Skip suite and slowest test sections |

### Examples

```bash
# CI mode for GitHub Actions
python summarize_playwright_results.py --ci

# Local run without LLM
python summarize_playwright_results.py --no-llm

# Compact output for quick review
python summarize_playwright_results.py --compact

# Custom results directory
python summarize_playwright_results.py --results /path/to/allure-results
```

---

## Understanding the Output

### Sample Output

```markdown
## 🎭 Playwright E2E Test Summary

### ✅ **ALL TESTS PASSED**

| Status | Count | Percentage |
|--------|-------|------------|
| ✅ Passed | 8 | 88.9% |
| ❌ Failed | 0 | 0.0% |
| ⏭️ Skipped | 1 | 11.1% |
| **Total** | **9** | **100%** |

### ⏱️ Performance Metrics

- **Total Duration:** 45.2s
- **Average Test Duration:** 5.0s
- **Pass Rate:** 88.9%

### 📦 Test Suites

| Suite | ✅ | ❌ | 💔 | ⏭️ |
|-------|-----|-----|-----|-----|
| chromium | 8 | 0 | 0 | 1 |

### 💡 Recommendations

1. Review 1 skipped test(s) to ensure they are intentionally disabled.
2. All tests passing - consider adding more edge case coverage.
```

### With Failures

```markdown
### ❌ **TESTS FAILED**

| Status | Count | Percentage |
|--------|-------|------------|
| ✅ Passed | 6 | 66.7% |
| ❌ Failed | 2 | 22.2% |
| ⏭️ Skipped | 1 | 11.1% |

### ❌ Failed Tests

**1. ❌ User can create a note**
- 📁 File: `note-with-fixture-and-api.spec.ts`
- 💬 Error: Expected title to be "My Note" but got "undefined"

**2. ❌ Login with invalid credentials**
- 📁 File: `login.spec.ts`
- 💬 Error: Timeout waiting for element "#error-message"
```

---

## Fine-Tuning LLM Parameters

### Configuration Block

```python
# LLM settings - tuned for concise, non-repetitive output
N_CTX = 4096          # Context window size
MAX_TOKENS = 300      # Maximum output tokens
TEMPERATURE = 0.15    # Randomness (0.0-2.0)
REPEAT_PENALTY = 1.3  # Penalize repetition (1.0-2.0)
TOP_P = 0.9           # Nucleus sampling
TOP_K = 40            # Top-k sampling
```

### Parameter Guide

| Parameter | Current | Range | Effect |
|-----------|---------|-------|--------|
| `N_CTX` | 4096 | 256-32768 | Context window size |
| `MAX_TOKENS` | 300 | 50-2000 | Max output length |
| `TEMPERATURE` | 0.15 | 0.0-2.0 | Lower = more deterministic |
| `REPEAT_PENALTY` | 1.3 | 0.0-2.0 | Higher = less repetition |
| `TOP_P` | 0.9 | 0.0-1.0 | Nucleus sampling threshold |
| `TOP_K` | 40 | 1-100 | Top-k token sampling |

### Recommended Settings

#### For Concise Output (Default)
```python
TEMPERATURE = 0.15
MAX_TOKENS = 300
REPEAT_PENALTY = 1.3
```

#### For More Creative Analysis
```python
TEMPERATURE = 0.4
MAX_TOKENS = 500
REPEAT_PENALTY = 1.1
```

#### For Strict Determinism
```python
TEMPERATURE = 0.0
MAX_TOKENS = 200
REPEAT_PENALTY = 1.5
```

---

## Prompt Engineering

### System Prompt

The script uses a carefully crafted system prompt:

```python
SYSTEM_PROMPT = """You are a QA engineer analyzing Playwright test results.

Generate 3-5 brief, actionable insights based on the test data below.

Rules:
- Output only a numbered list (1., 2., 3., ...).
- Each item must be one sentence.
- Focus on patterns, root causes, and next steps.
- Be specific - mention test names or suites when relevant.
- No repetition, no fluff, no greetings."""
```

### Prompt Structure

```python
def build_llm_prompt(stats, failures):
    summary = f"Tests: {total} total, {passed} passed, {failed} failed..."
    
    return f"""{SYSTEM_PROMPT}

Data: {summary}

Insights:"""
```

### Best Practices

1. **Be Specific**: Include exact numbers and test names
2. **Set Constraints**: Limit output format (numbered list only)
3. **Use Stop Sequences**: Prevent rambling (`stop=["===", "---"]`)
4. **Provide Context**: Include suite names and error patterns

### Customizing the Prompt

To change the LLM's focus, modify `SYSTEM_PROMPT`:

```python
# Focus on performance issues
SYSTEM_PROMPT = """You are a performance engineer.
Analyze the test durations and suggest optimizations.
Output 3-5 numbered recommendations."""

# Focus on failure patterns
SYSTEM_PROMPT = """You are a QA lead reviewing test failures.
Identify patterns and root causes.
Output 3-5 numbered insights."""
```

---

## CI Integration

### GitHub Actions Workflow

Add this step to `.github/workflows/playwright.yml`:

```yaml
# Generate Playwright Test Summary (before Schemathesis)
- name: Generate Playwright Summary
  if: always()
  working-directory: e2e
  run: |
    python scripts/summarize_playwright_results.py \
      --ci \
      --results allure-results \
      >> $GITHUB_STEP_SUMMARY || echo "⚠️ Could not generate Playwright summary" >> $GITHUB_STEP_SUMMARY

# Then Schemathesis summary follows...
- name: Generate Schemathesis Summary
  if: always()
  working-directory: e2e
  run: |
    python scripts/summarize_schemathesis_results.py \
      --ci \
      --results schemathesis/allure-results \
      >> $GITHUB_STEP_SUMMARY
```

### Full Workflow Order

```yaml
# 1. Run Playwright tests
- name: Run Playwright tests
  run: npx playwright test
  continue-on-error: true

# 2. Generate Playwright summary (FIRST in job summary)
- name: Generate Playwright Summary
  if: always()
  run: python scripts/summarize_playwright_results.py --ci >> $GITHUB_STEP_SUMMARY

# 3. Run Schemathesis tests
- name: Run Schemathesis API tests
  run: python run_schemathesis.py
  continue-on-error: true

# 4. Generate Schemathesis summary (SECOND in job summary)
- name: Generate Schemathesis Summary
  if: always()
  run: python scripts/summarize_schemathesis_results.py --ci >> $GITHUB_STEP_SUMMARY

# 5. Generate Allure reports and upload artifacts
```

### CI Output Example

The GitHub Actions job summary will show:

```markdown
## 🎭 Playwright E2E Test Summary

### ✅ **ALL TESTS PASSED**

| Status | Count | Percentage |
|--------|-------|------------|
| ✅ Passed | 9 | 100.0% |
| **Total** | **9** | **100%** |

### ⏱️ Performance Metrics
- **Total Duration:** 45.2s
- **Pass Rate:** 100.0%

### 💡 Recommendations
1. All tests passing - consider adding more edge case coverage.

---

## 🔬 Schemathesis API Test Summary
...
```

---

## Customization

### Adding Custom Recommendations

Modify `generate_deterministic_recommendations()`:

```python
def generate_deterministic_recommendations(stats):
    recommendations = []
    
    # Add your custom rules
    if stats["total"] < 10:
        recommendations.append(
            "Test coverage is low - add more E2E tests for critical user flows."
        )
    
    if stats["avg_duration_ms"] > 30000:
        recommendations.append(
            "Tests are slow - consider using API setup instead of UI flows."
        )
    
    # ... existing logic
```

### Custom Status Icons

```python
STATUS_ICONS = {
    "passed": "✅",
    "failed": "❌",
    "broken": "💔",
    "skipped": "⏭️",
    "unknown": "❓",
}

# Change to text-based for accessibility
STATUS_ICONS = {
    "passed": "[PASS]",
    "failed": "[FAIL]",
    "broken": "[BROKEN]",
    "skipped": "[SKIP]",
    "unknown": "[?]",
}
```

### Filtering Results

To analyze only certain tests:

```python
def filter_results(results, pattern):
    """Filter results by test name pattern."""
    import re
    return [r for r in results if re.search(pattern, r["name"])]

# In main():
results = filter_results(results, r"login|auth")  # Only auth tests
```

---

## Troubleshooting

### Common Issues

#### 1. "No result files found"

```bash
# Ensure Playwright ran with allure reporter
npx playwright test

# Check files exist
ls e2e/allure-results/*-result.json
```

#### 2. "Could not parse result file"

```bash
# Validate JSON
python -c "import json; json.load(open('file.json'))"
```

#### 3. LLM output is empty

```bash
# Check model path
grep MODEL_PATH scripts/summarize_playwright_results.py

# Verify file exists
ls -la "/path/to/model.gguf"
```

#### 4. Output is too long/short

Adjust `MAX_TOKENS`:
```python
MAX_TOKENS = 500  # Increase for longer output
MAX_TOKENS = 150  # Decrease for shorter output
```

#### 5. Repetitive LLM output

Increase repeat penalty:
```python
REPEAT_PENALTY = 1.5  # Higher = less repetition
```

### Debug Mode

Run with verbose output:

```bash
# See parsing progress
python summarize_playwright_results.py 2>&1 | head -20

# Check raw JSON
cat allure-results/*-result.json | python -m json.tool | head -50
```

---

## Resources

- [Playwright Documentation](https://playwright.dev/)
- [Allure Framework](https://allurereport.org/)
- [allure-playwright Reporter](https://www.npmjs.com/package/allure-playwright)
- [llama-cpp-python](https://github.com/abetlen/llama-cpp-python)
- [LLM Summarizer Guide](./LLM_SUMMARIZER_GUIDE.md)

---

**Built with ❤️ for intelligent test reporting**
