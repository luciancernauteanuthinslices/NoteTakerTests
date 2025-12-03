# 🤖 LLM Test Report Summarizer Guide

A comprehensive guide for using **llama-cpp-python** to generate intelligent summaries of test results, integrated into the NoteTaker test automation framework.

---

## 📚 Table of Contents

- [Overview](#overview)
- [What is llama-cpp-python?](#what-is-llama-cpp-python)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Downloading the Model](#downloading-the-model)
- [Running Your First LLM Test](#running-your-first-llm-test)
- [The Summarizer Script](#the-summarizer-script)
- [Fine-Tuning LLM Parameters](#fine-tuning-llm-parameters)
- [Using with Multiple Report Types](#using-with-multiple-report-types)
- [CI Integration](#ci-integration)
- [Troubleshooting](#troubleshooting)

---

## Overview

This integration provides LLM-powered test result summarization that:

- ✅ **Parses JUnit XML** from Schemathesis (or any test framework)
- ✅ **Generates intelligent recommendations** using a local LLM
- ✅ **Runs entirely offline** - no API keys or cloud services needed
- ✅ **Produces deterministic fallback** when LLM is unavailable (CI mode)
- ✅ **Outputs to GitHub Actions job summary** in CI pipelines

---

## What is llama-cpp-python?

[llama-cpp-python](https://github.com/abetlen/llama-cpp-python) is a Python binding for [llama.cpp](https://github.com/ggerganov/llama.cpp), a high-performance C++ implementation for running Large Language Models locally.

### Why llama-cpp-python?

| Feature | Benefit |
|---------|---------|
| **Local execution** | No API keys, no cloud costs, no data privacy concerns |
| **GGUF format** | Optimized quantized models that run on consumer hardware |
| **Metal/CUDA support** | GPU acceleration on macOS (Metal) and NVIDIA (CUDA) |
| **Small models** | 0.5B-7B parameter models run on laptops |
| **Python bindings** | Easy integration with existing Python scripts |

### How It Works

1. **Model file** (`.gguf`) is loaded into memory
2. **Prompt** is tokenized and fed to the model
3. **Inference** generates text token-by-token
4. **Output** is post-processed and returned

---

## Project Structure

```
NoteTaker/
├── e2e/
│   ├── scripts/                      # 🤖 LLM scripts folder
│   │   ├── run_llm_once.py           # Simple LLM test script
│   │   ├── summarize_schemathesis_results.py  # Full summarizer
│   │   └── LLM_SUMMARIZER_GUIDE.md   # This documentation
│   │
│   ├── schemathesis/
│   │   ├── venv/                     # Python virtual environment
│   │   ├── allure-results/           # JUnit XML output
│   │   └── requirements.txt          # Python dependencies
│   │
│   └── openapi.json                  # OpenAPI specification
│
└── .github/workflows/
    └── playwright.yml                # CI workflow with LLM summary
```

---

## Setup & Installation

### Prerequisites

- **Python 3.10+** (3.12 recommended)
- **pip** (Python package manager)
- **~500MB disk space** for the model file

### Step 1: Use the Existing Virtual Environment

The Schemathesis venv already has the dependencies. If not, create one:

```bash
# Navigate to schemathesis folder (inside e2e)
cd e2e/schemathesis

# Create virtual environment (if it doesn't exist)
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### Step 2: Install llama-cpp-python

```bash
# With virtual environment activated
pip install llama-cpp-python

# For macOS with Metal GPU acceleration (recommended):
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python --force-reinstall --no-cache-dir

# For NVIDIA GPU (CUDA):
CMAKE_ARGS="-DLLAMA_CUDA=on" pip install llama-cpp-python --force-reinstall --no-cache-dir

# Verify installation
python -c "from llama_cpp import Llama; print('OK')"
```

### Step 3: Update requirements.txt (optional)

If you want to track the dependency:

```bash
pip freeze | grep llama >> requirements.txt
```

---

## Downloading the Model

We use **Qwen2.5-0.5B-Instruct** - a small but capable instruction-following model.

### Why Qwen2.5-0.5B?

| Aspect | Value |
|--------|-------|
| **Size** | ~400MB (Q4_0 quantization) |
| **Parameters** | 0.5 billion |
| **Speed** | Fast inference on CPU |
| **Quality** | Good for structured tasks like summarization |

### Download from Hugging Face

1. Visit: [Qwen2.5-0.5B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF)

2. Download the quantized model file:
   - **Recommended:** `qwen2.5-0.5b-instruct-q4_0.gguf` (~400MB)
   - Alternative: `qwen2.5-0.5b-instruct-q8_0.gguf` (~600MB, higher quality)

3. Save to a known location, e.g.:
   ```
   ~/Documents/LLM Models/Qwen2.5-0.5B-Instruct-Q4_0.gguf
   ```

### Direct Download Link

```bash
# Create directory
mkdir -p ~/Documents/"LLM Models"

# Download with wget or curl
wget -O ~/Documents/"LLM Models"/Qwen2.5-0.5B-Instruct-Q4_0.gguf \
  "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF/resolve/main/qwen2.5-0.5b-instruct-q4_0.gguf"
```

### Update Model Path in Scripts

Edit the `MODEL_PATH` in both scripts to match your download location:

```python
# In run_llm_once.py and summarize_schemathesis_results.py
MODEL_PATH = "/path/to/your/Qwen2.5-0.5B-Instruct-Q4_0.gguf"
```

---

## Running Your First LLM Test

### The `run_llm_once.py` Script

This is a minimal script to verify your LLM setup works:

```python
#!/usr/bin/env python
import sys
from llama_cpp import Llama

MODEL_PATH = "/path/to/Qwen2.5-0.5B-Instruct-Q4_0.gguf"

if len(sys.argv) < 2:
    print("Usage: run_llm_once.py '<prompt>'", file=sys.stderr)
    sys.exit(1)

prompt = sys.argv[1]

llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=256,        # Context window size
    verbose=False,    # Suppress loading messages
)

output = llm(
    prompt,
    max_tokens=2056,  # Maximum output length
    temperature=2.0,  # High = more creative
)

text = output["choices"][0]["text"].strip()
print(text)
```

### Run It

```bash
# Activate venv
cd e2e/schemathesis
source venv/bin/activate

# Run a simple test
python ../scripts/run_llm_once.py "What is HTTP status code 405?"
```

### Expected Output

```
HTTP 405 Method Not Allowed indicates that the request method 
is known by the server but is not supported by the target resource.
```

---

## The Summarizer Script

### `summarize_schemathesis_results.py`

This script parses JUnit XML test results and generates actionable recommendations.

### How It Works

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  JUnit XML      │────▶│  Parse & Categorize │────▶│  Deterministic  │
│  (allure-results)│     │  Failures           │     │  Recommendations│
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                │
                                ▼
                        ┌──────────────────┐
                        │  LLM (optional)  │
                        │  Additional Tips │
                        └──────────────────┘
                                │
                                ▼
                        ┌──────────────────┐
                        │  Markdown Report │
                        │  (stdout/summary)│
                        └──────────────────┘
```

### Key Functions

| Function | Purpose |
|----------|---------|
| `parse_junit_xml()` | Extract test failures from XML |
| `categorize_failures()` | Group failures by type (404 vs 405, missing headers, etc.) |
| `generate_deterministic_recommendations()` | Rule-based recommendations (always works) |
| `run_llm()` | Optional LLM-generated suggestions |
| `generate_markdown_report()` | Format output for GitHub Actions |

### Usage

```bash
# Activate venv
cd e2e/schemathesis
source venv/bin/activate

# Default run (with LLM if available)
python ../scripts/summarize_schemathesis_results.py

# CI mode (no LLM, clean markdown output)
python ../scripts/summarize_schemathesis_results.py --ci

# Custom paths
python ../scripts/summarize_schemathesis_results.py \
  --results ./allure-results \
  --openapi ../openapi.json

# Skip LLM even locally
python ../scripts/summarize_schemathesis_results.py --no-llm
```

### Sample Output

```markdown
## 🔬 Schemathesis API Test Summary

## Summary
- **55 failures** across 56 tests
- **Missing Allow header on 405:** GET /, POST /notes, DELETE /notes/{id} (+52 more)

## OpenAPI Spec
- **12 paths** defined in spec
- **Methods:** DELETE: 3, GET: 4, POST: 7

## 🔧 Recommendations

1. Add `Allow` header to all 405 responses listing supported methods (RFC 9110 requirement).
2. Configure your web server/framework (e.g., FastAPI, nginx) to automatically include `Allow` header.
3. Update OpenAPI spec to document all supported methods per endpoint.
4. Add integration tests that verify correct HTTP status codes.
```

---

## Fine-Tuning LLM Parameters

The script has several parameters you can adjust to control LLM behavior:

### Configuration Block

```python
# LLM settings
N_CTX = 8200          # Context window size
MAX_TOKENS = 230      # Maximum output tokens
TEMPERATURE = 0.1     # Randomness (0.0-2.0)
REPEAT_PENALTY = 0.8  # Penalize repetition (0.0-2.0)
```

### Parameter Guide

| Parameter | Range | Effect | Recommended |
|-----------|-------|--------|-------------|
| `N_CTX` | 256-32768 | How much text the model can "see" | 8200 for large reports |
| `MAX_TOKENS` | 50-2000 | Maximum output length | 200-300 for summaries |
| `TEMPERATURE` | 0.0-2.0 | Creativity vs determinism | 0.1-0.3 for factual output |
| `REPEAT_PENALTY` | 0.0-2.0 | Prevent repetitive text | 0.8-1.2 |

### Tuning for Different Scenarios

#### More Concise Output
```python
MAX_TOKENS = 150
TEMPERATURE = 0.1
```

#### More Creative Suggestions
```python
MAX_TOKENS = 500
TEMPERATURE = 0.7
```

#### Prevent Repetition
```python
REPEAT_PENALTY = 1.5  # Higher = less repetition
```

#### Larger Test Reports
```python
N_CTX = 16000  # Increase context window
```

### Prompt Engineering

The system prompt controls output format:

```python
SYSTEM_PROMPT = """You are an expert in HTTP semantics and OpenAPI.

From the issues below, produce 8–10 recommendations that:
- Fix incorrect status codes
- Align behavior with the OpenAPI spec
- Improve validation and error handling

Rules:
- Output only a numbered list (1., 2., 3., 4., 5., …).
- One sentence per item.
- Mention HTTP codes and OpenAPI when relevant.
- No extra commentary, no headings."""
```

**Tips for better prompts:**
- Be explicit about output format
- Provide few-shot examples
- Limit scope to prevent rambling
- Use stop sequences (`stop=["===", "---"]`)

---

## Using with Multiple Report Types

The summarizer architecture can be extended to other test frameworks.

### Adapting for Other JUnit XML Sources

Any tool that produces JUnit XML can use this summarizer:

| Tool | XML Location | Adaptation Needed |
|------|--------------|-------------------|
| **Schemathesis** | `allure-results/junit*.xml` | None (default) |
| **pytest** | `junit.xml` | Change `find_junit_xml_files()` pattern |
| **Jest** | `junit.xml` | Change pattern |
| **Playwright** | `results.xml` | Change pattern |

### Example: Playwright JUnit XML

```python
# Modify find_junit_xml_files() for Playwright
def find_junit_xml_files(results_dir: Path) -> list[Path]:
    patterns = [
        str(results_dir / "junit*.xml"),
        str(results_dir / "results.xml"),
        str(results_dir / "**/*.xml"),
    ]
    files = []
    for pattern in patterns:
        files.extend(glob.glob(pattern, recursive=True))
    return [Path(f) for f in sorted(set(files))]
```

### Creating a Generic Summarizer

```python
# summarize_any_junit.py
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", required=True, help="Path to JUnit XML directory")
    parser.add_argument("--type", choices=["schemathesis", "playwright", "pytest"], default="schemathesis")
    args = parser.parse_args()
    
    # Load appropriate categorization rules based on type
    if args.type == "schemathesis":
        categories = SCHEMATHESIS_CATEGORIES
    elif args.type == "playwright":
        categories = PLAYWRIGHT_CATEGORIES
    # ... etc
```

---

## CI Integration

### GitHub Actions Workflow

The summarizer runs in CI and outputs to the job summary:

```yaml
# .github/workflows/playwright.yml

- name: Generate Schemathesis Summary
  if: always()
  working-directory: e2e
  run: |
    python scripts/summarize_schemathesis_results.py \
      --ci \
      --results schemathesis/allure-results \
      --openapi openapi.json \
      >> $GITHUB_STEP_SUMMARY || echo "⚠️ Could not generate summary" >> $GITHUB_STEP_SUMMARY
```

### How CI Mode Works

| Mode | LLM | Output | Use Case |
|------|-----|--------|----------|
| Default | Yes (if available) | Decorated console | Local development |
| `--ci` | No | Clean markdown | GitHub Actions |
| `--no-llm` | No | Decorated console | Local without LLM |

### CI Output Example

In GitHub Actions, the job summary will show:

```markdown
## 🔬 Schemathesis API Test Summary

## Summary
- **55 failures** across 56 tests
- **Missing Allow header on 405:** GET /, POST /notes (+53 more)

## 🔧 Recommendations
1. Add `Allow` header to all 405 responses...
2. Configure your web server/framework...
```

### Why No LLM in CI?

- **No model file** - GGUF files are large (~400MB) and not committed to git
- **Deterministic output** - CI should produce consistent results
- **Speed** - LLM inference adds 5-30 seconds
- **Dependencies** - `llama-cpp-python` requires compilation

The deterministic recommendations provide the same actionable insights without the LLM.

---

## Troubleshooting

### Common Issues

#### 1. "No module named 'llama_cpp'"

```bash
# Make sure venv is activated
source venv/bin/activate

# Install the package
pip install llama-cpp-python
```

#### 2. "Model file not found"

```bash
# Check the path in the script
grep MODEL_PATH scripts/summarize_schemathesis_results.py

# Verify file exists
ls -la "/path/to/your/model.gguf"
```

#### 3. "Metal/CUDA not working"

```bash
# Reinstall with GPU support
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python --force-reinstall --no-cache-dir
```

#### 4. LLM output is repetitive

Adjust parameters:
```python
REPEAT_PENALTY = 1.5  # Increase from 0.8
MAX_TOKENS = 200      # Decrease to limit output
TEMPERATURE = 0.2     # Slight increase for variety
```

#### 5. LLM output is cut off

```python
MAX_TOKENS = 500  # Increase output limit
N_CTX = 16000     # Increase context window
```

#### 6. Slow inference

```bash
# Use GPU acceleration (macOS)
CMAKE_ARGS="-DLLAMA_METAL=on" pip install llama-cpp-python --force-reinstall

# Or use a smaller model
# Download qwen2.5-0.5b instead of larger variants
```

### Debug Mode

Run with verbose output:

```bash
# In Python, set verbose=True
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=N_CTX,
    verbose=True,  # Show loading progress
)
```

---

## Resources

- [llama-cpp-python GitHub](https://github.com/abetlen/llama-cpp-python)
- [llama.cpp GitHub](https://github.com/ggerganov/llama.cpp)
- [Qwen2.5 Models on Hugging Face](https://huggingface.co/Qwen)
- [GGUF Format Specification](https://github.com/ggerganov/ggml/blob/master/docs/gguf.md)
- [Schemathesis Documentation](https://schemathesis.readthedocs.io/)

---

**Built with ❤️ for intelligent test automation**
