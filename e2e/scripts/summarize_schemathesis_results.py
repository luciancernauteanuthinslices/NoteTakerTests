#!/usr/bin/env python3
"""
Summarize Schemathesis JUnit XML results using a local LLM (llama.cpp).

Usage:
    python summarize_schemathesis_results.py [path/to/allure-results] [path/to/openapi.json]

If no path is given, defaults to ../schemathesis/allure-results/
OpenAPI spec defaults to ../openapi.json
"""

import sys
import os
import glob
import re
import html
import json
import argparse
from pathlib import Path
from xml.etree import ElementTree as ET

# ═══════════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════════

# LLM Model Path - configurable via environment variable
DEFAULT_MODEL_PATH = "/Users/lucian.cernauteanuthinslices.com/Documents/LLM Models/Qwen2.5-0.5B-Instruct-Q4_0.gguf"
MODEL_PATH = os.environ.get("LLM_MODEL_PATH", DEFAULT_MODEL_PATH)

# Default paths (relative to this script)
SCRIPT_DIR = Path(__file__).parent.resolve()
ALLURE_BASE_DIR = SCRIPT_DIR.parent / "schemathesis" / "allure-results"
DEFAULT_OPENAPI_PATH = SCRIPT_DIR.parent / "openapi.json"


# ═══════════════════════════════════════════════════════════════════════════════
# Timestamped Run Detection
# ═══════════════════════════════════════════════════════════════════════════════

def find_latest_run(base_dir: Path) -> Path:
    """
    Find the latest run folder in the allure-results directory.
    
    Checks for:
    1. .current-run file (written by test runner)
    2. Latest run-* folder by name (timestamp-based sorting)
    3. Falls back to base_dir if no run folders exist
    """
    if not base_dir.exists():
        return base_dir
    
    # Check for .current-run marker file
    current_run_file = base_dir / ".current-run"
    if current_run_file.exists():
        run_id = current_run_file.read_text().strip()
        run_dir = base_dir / run_id
        if run_dir.exists():
            return run_dir
    
    # Find all run-* directories and sort by name (timestamp order)
    run_dirs = sorted(
        [d for d in base_dir.iterdir() if d.is_dir() and d.name.startswith("run-")],
        reverse=True  # Latest first
    )
    
    if run_dirs:
        return run_dirs[0]
    
    # Fallback: check if results are directly in base_dir (legacy format)
    if list(base_dir.glob("junit*.xml")):
        return base_dir
    
    return base_dir


def get_default_results_dir() -> Path:
    """Get the default results directory (latest run)."""
    return find_latest_run(ALLURE_BASE_DIR)


# LLM settings
N_CTX = 8200  # Context window (increase if you have more failures)
MAX_TOKENS = 230  # Max output tokens (shorter to avoid repetition)
TEMPERATURE = 0.1  # Low temperature for more deterministic summaries
REPEAT_PENALTY = 0.8  # Higher penalty to reduce repetition


# ═══════════════════════════════════════════════════════════════════════════════
# Step 1: Parse JUnit XML and extract failures
# ═══════════════════════════════════════════════════════════════════════════════

def find_junit_xml_files(results_dir: Path) -> list[Path]:
    """Find all JUnit XML files in the given directory."""
    pattern = str(results_dir / "junit*.xml")
    files = glob.glob(pattern)
    return [Path(f) for f in sorted(files)]


def clean_failure_message(raw_message: str) -> str:
    """
    Clean up the raw failure message:
    - Unescape HTML entities
    - Remove verbose HTML body content
    - Keep only the essential failure info
    """
    # Unescape HTML entities
    msg = html.unescape(raw_message)
    
    # Remove full HTML responses (keep just the status line)
    msg = re.sub(r'`<!doctype html>.*?// Output truncated\.\.\.`', '[HTML response truncated]', msg, flags=re.DOTALL | re.IGNORECASE)
    msg = re.sub(r'`<!doctype html>.*?`', '[HTML response]', msg, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove curl reproduce commands to save tokens
    msg = re.sub(r'Reproduce with:\s*\n\s*curl[^\n]+', '', msg)
    
    # Collapse multiple newlines
    msg = re.sub(r'\n{3,}', '\n\n', msg)
    
    return msg.strip()


def extract_failure_summary(raw_message: str) -> str:
    """
    Extract a one-line summary from a failure message.
    Looks for patterns like "- Missing header not rejected" or "- Unsupported methods".
    """
    # Find the category line (starts with "- ")
    categories = re.findall(r'^- (.+)$', raw_message, re.MULTILINE)
    if categories:
        return "; ".join(categories[:3])  # Take up to 3 categories
    
    # Fallback: first meaningful line
    lines = [l.strip() for l in raw_message.split('\n') if l.strip() and not l.startswith('Reproduce')]
    return lines[0][:100] if lines else "Unknown failure"


def parse_junit_xml(xml_path: Path) -> dict:
    """
    Parse a JUnit XML file and extract test results.
    
    Returns:
        {
            "total_tests": int,
            "total_failures": int,
            "failures": [
                {"endpoint": "METHOD /path", "summary": "...", "details": "..."},
                ...
            ]
        }
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    # Get overall stats from <testsuites> or <testsuite>
    if root.tag == "testsuites":
        total_tests = int(root.get("tests", 0))
        total_failures = int(root.get("failures", 0))
    else:
        total_tests = int(root.get("tests", 0))
        total_failures = int(root.get("failures", 0))
    
    failures = []
    
    # Find all testcase elements
    for testcase in root.iter("testcase"):
        failure_elem = testcase.find("failure")
        if failure_elem is not None:
            endpoint = testcase.get("name", "Unknown endpoint")
            raw_message = failure_elem.get("message", "") or failure_elem.text or ""
            
            summary = extract_failure_summary(raw_message)
            details = clean_failure_message(raw_message)
            
            failures.append({
                "endpoint": endpoint,
                "summary": summary,
                "details": details,
            })
    
    return {
        "total_tests": total_tests,
        "total_failures": total_failures,
        "failures": failures,
    }


def categorize_failures(failures: list[dict]) -> dict[str, list[dict]]:
    """
    Pre-categorize failures by type with granular sub-types.
    Returns a dict: category -> list of failure dicts with endpoint and sub_type.
    """
    categories = {
        "Missing header not rejected (401 vs 406)": [],
        "Missing Allow header on 405": [],
        "Wrong status code (404 vs 405)": [],
        "Schema-compliant request rejected": [],
        "Other failures": [],
    }
    
    for f in failures:
        details_lower = f.get('details', '').lower()
        summary_lower = f['summary'].lower()
        endpoint = f['endpoint']
        
        # Extract sub-type from details
        sub_type = None
        if 'allow' in details_lower and 'header' in details_lower:
            sub_type = "missing_allow_header"
        elif '404' in details_lower and '405' in details_lower:
            sub_type = "404_instead_of_405"
        
        entry = {"endpoint": endpoint, "sub_type": sub_type, "details": f.get('details', '')}
        
        if 'missing header' in summary_lower:
            categories["Missing header not rejected (401 vs 406)"].append(entry)
        elif 'unsupported method' in summary_lower:
            # Further categorize unsupported methods
            if 'allow' in details_lower and 'header' in details_lower:
                categories["Missing Allow header on 405"].append(entry)
            else:
                categories["Wrong status code (404 vs 405)"].append(entry)
        elif 'schema-compliant' in summary_lower or 'rejected' in summary_lower:
            categories["Schema-compliant request rejected"].append(entry)
        else:
            categories["Other failures"].append(entry)
    
    # Remove empty categories
    return {k: v for k, v in categories.items() if v}


def format_failures_for_llm(failures: list[dict], max_chars: int = 3000) -> str:
    """
    Format failures into a pre-categorized text block for the LLM.
    This reduces the LLM's workload by doing categorization upfront.
    """
    categories = categorize_failures(failures)
    
    lines = []
    for category, entries in categories.items():
        # Deduplicate endpoints within category
        unique_endpoints = sorted(set(e["endpoint"] for e in entries))
        lines.append(f"**{category}:** ({len(entries)} occurrences)")
        for ep in unique_endpoints[:10]:  # Limit to 10 per category
            lines.append(f"  - {ep}")
        if len(unique_endpoints) > 10:
            lines.append(f"  - ... and {len(unique_endpoints) - 10} more endpoints")
        lines.append("")
    
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# OpenAPI Spec Loading
# ═══════════════════════════════════════════════════════════════════════════════

def load_openapi_spec(openapi_path: Path) -> dict:
    """Load and parse the OpenAPI spec."""
    if not openapi_path.exists():
        print(f"OpenAPI spec not found: {openapi_path}", file=sys.stderr)
        return {}
    
    with open(openapi_path, 'r') as f:
        return json.load(f)


def extract_openapi_methods(openapi_spec: dict) -> dict[str, list[str]]:
    """
    Extract defined HTTP methods per path from OpenAPI spec.
    Returns: {path: [methods]}
    """
    paths = openapi_spec.get("paths", {})
    result = {}
    
    http_methods = {"get", "post", "put", "delete", "patch", "head", "options", "trace"}
    
    for path, path_item in paths.items():
        methods = [m.upper() for m in path_item.keys() if m.lower() in http_methods]
        if methods:
            result[path] = methods
    
    return result


def normalize_path(endpoint: str) -> str:
    """
    Normalize endpoint path for matching with OpenAPI.
    E.g., 'GET /trials/123' -> '/trials/{trial_id}'
    """
    # Extract just the path part (remove method prefix)
    parts = endpoint.split(' ', 1)
    if len(parts) == 2:
        path = parts[1]
    else:
        path = endpoint
    
    # Replace numeric IDs with placeholders
    path = re.sub(r'/\d+', '/{id}', path)
    # Replace UUIDs
    path = re.sub(r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/{id}', path, flags=re.IGNORECASE)
    
    return path


# ═══════════════════════════════════════════════════════════════════════════════
# Step 2 & 3: Build the prompt with few-shot examples
# ═══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = SYSTEM_PROMPT = """You are an expert in HTTP semantics and OpenAPI.

From the issues below, produce 8–10 recommendations that:
- Fix incorrect status codes
- Align behavior with the OpenAPI spec
- Improve validation and error handling

Rules:
- Output only a numbered list (1., 2., 3., 4., 5., …).
- One sentence per item.
- Mention HTTP codes and OpenAPI when relevant.
- No extra commentary, no headings."""


FEW_SHOT_EXAMPLE = """Example:
Issues: Unsupported methods return 404 instead of 405. Missing headers return 401 instead of 406.
Recommendations:
1. Return HTTP 405 for unsupported HTTP methods.
2. Return HTTP 406 when required headers are missing.
3. Update OpenAPI spec to match actual behavior."""


def build_prompt(failures_text: str, total_tests: int, total_failures: int) -> str:
    """Build a minimal prompt asking only for recommendations."""
    return f"""{SYSTEM_PROMPT}

{FEW_SHOT_EXAMPLE}

Issues: {failures_text}
Recommendations:"""


def generate_python_summary(failures: list[dict], total_tests: int, total_failures: int, openapi_methods: dict = None) -> str:
    """Generate the summary section using Python (no LLM needed)."""
    categories = categorize_failures(failures)
    
    lines = [
        f"## Summary",
        f"- **{total_failures} failures** across {total_tests} tests",
        "",
    ]
    
    for category, entries in categories.items():
        unique_endpoints = sorted(set(e["endpoint"] for e in entries))
        endpoint_list = ", ".join(unique_endpoints[:5])
        if len(unique_endpoints) > 5:
            endpoint_list += f" (+{len(unique_endpoints) - 5} more)"
        lines.append(f"- **{category}:** {endpoint_list}")
    
    # Add OpenAPI context if available
    if openapi_methods:
        lines.append("")
        lines.append(f"## OpenAPI Spec")
        lines.append(f"- **{len(openapi_methods)} paths** defined in spec")
        method_counts = {}
        for methods in openapi_methods.values():
            for m in methods:
                method_counts[m] = method_counts.get(m, 0) + 1
        method_summary = ", ".join(f"{m}: {c}" for m, c in sorted(method_counts.items()))
        lines.append(f"- **Methods:** {method_summary}")
    
    return "\n".join(lines)


def generate_deterministic_recommendations(failures: list[dict], openapi_methods: dict = None) -> str:
    """
    Generate actionable recommendations deterministically (no LLM).
    This is more reliable than the small LLM for structured output.
    """
    categories = categorize_failures(failures)
    recommendations = []
    
    # Analyze each category and generate specific recommendations
    if "Missing Allow header on 405" in categories:
        entries = categories["Missing Allow header on 405"]
        endpoints = sorted(set(e["endpoint"] for e in entries))[:3]
        recommendations.append(
            f"Add `Allow` header to all 405 responses listing supported methods (RFC 9110 requirement). "
            f"Affected: {', '.join(endpoints)}{'...' if len(entries) > 3 else ''}"
        )
        recommendations.append(
            "Configure your web server/framework (e.g., FastAPI, nginx) to automatically include `Allow` header on 405 responses."
        )
    
    if "Wrong status code (404 vs 405)" in categories:
        entries = categories["Wrong status code (404 vs 405)"]
        endpoints = sorted(set(e["endpoint"] for e in entries))[:3]
        recommendations.append(
            f"Return HTTP 405 (Method Not Allowed) instead of 404 for unsupported methods. "
            f"Affected: {', '.join(endpoints)}{'...' if len(entries) > 3 else ''}"
        )
        recommendations.append(
            "Add a catch-all route handler that returns 405 for undefined methods on existing paths."
        )
        if openapi_methods:
            recommendations.append(
                f"Cross-check your router configuration against the OpenAPI spec ({len(openapi_methods)} paths defined)."
            )
    
    if "Missing header not rejected (401 vs 406)" in categories:
        entries = categories["Missing header not rejected (401 vs 406)"]
        recommendations.append(
            "Return HTTP 406 (Not Acceptable) when required Accept/Content-Type headers are missing."
        )
        recommendations.append(
            "Add middleware to validate required headers before processing requests."
        )
    
    if "Schema-compliant request rejected" in categories:
        recommendations.append(
            "Review request validation logic - schema-compliant requests should not be rejected."
        )
        recommendations.append(
            "Ensure OpenAPI schema matches actual API validation rules."
        )
    
    # General recommendations
    if openapi_methods:
        recommendations.append(
            "Update OpenAPI spec to document all supported methods per endpoint, or update API to match spec."
        )
    
    recommendations.append(
        "Add integration tests that verify correct HTTP status codes for unsupported methods."
    )
    
    # Format as numbered list
    return "\n".join(f"{i+1}. {rec}" for i, rec in enumerate(recommendations[:10]))


# ═══════════════════════════════════════════════════════════════════════════════
# Step 4: Run the LLM (optional, only when not in CI mode)
# ═══════════════════════════════════════════════════════════════════════════════

def run_llm(prompt: str) -> str:
    """Load the model and generate a summary."""
    try:
        from llama_cpp import Llama
    except ImportError:
        return ""  # LLM not available
    
    if not Path(MODEL_PATH).exists():
        return ""  # Model file not found
    
    print("Loading LLM model...", file=sys.stderr)
    llm = Llama(
        model_path=MODEL_PATH,
        n_ctx=N_CTX,
        verbose=False,
    )
    
    print("Generating summary...", file=sys.stderr)
    output = llm(
        prompt,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
        repeat_penalty=REPEAT_PENALTY,
        stop=["===", "---", "Input:"],  # Stop at section markers
    )
    
    raw_text = output["choices"][0]["text"].strip()
    return post_process_output(raw_text)


def post_process_output(text: str) -> str:
    """
    Clean up LLM output:
    - Keep only the first 10 recommendations
    - Remove any "Issues:" lines (LLM sometimes echoes input)
    - Trim trailing incomplete content
    """
    lines = text.split('\n')
    result_lines = []
    recommendation_count = 0
    
    for line in lines:
        stripped = line.strip()
        
        # Skip lines that echo the input or are section headers
        if stripped.startswith('Issues:') or stripped.startswith('Input:'):
            continue
        if '## Recommendations' in line or 'Recommendations:' in stripped:
            continue
        
        # Check if this is a numbered recommendation
        if re.match(r'^\d+\.', stripped):
            recommendation_count += 1
            if recommendation_count <= 10:
                result_lines.append(line)
            else:
                break  # Stop after 10 recommendations
    
    return '\n'.join(result_lines).strip()


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Summarize Schemathesis JUnit XML results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Local run with LLM:
  python summarize_schemathesis_results.py
  
  # CI mode (no LLM, clean markdown output):
  python summarize_schemathesis_results.py --ci
  
  # Custom paths:
  python summarize_schemathesis_results.py --results ./allure-results --openapi ./openapi.json
"""
    )
    parser.add_argument(
        "--ci", 
        action="store_true",
        help="CI mode: clean markdown output, no LLM, no progress messages"
    )
    parser.add_argument(
        "--results", "-r",
        type=Path,
        default=None,
        help=f"Path to allure-results directory (default: latest run in {ALLURE_BASE_DIR})"
    )
    parser.add_argument(
        "--openapi", "-o",
        type=Path,
        default=DEFAULT_OPENAPI_PATH,
        help=f"Path to OpenAPI spec JSON (default: {DEFAULT_OPENAPI_PATH})"
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Skip LLM recommendations (use deterministic only)"
    )
    
    # Support legacy positional arguments for backwards compatibility
    parser.add_argument("legacy_results", nargs="?", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("legacy_openapi", nargs="?", type=Path, help=argparse.SUPPRESS)
    
    args = parser.parse_args()
    
    # Handle legacy positional arguments
    if args.legacy_results:
        args.results = args.legacy_results
    if args.legacy_openapi:
        args.openapi = args.legacy_openapi
    
    # Resolve results directory - find latest run if needed
    if args.results is None:
        args.results = get_default_results_dir()
    elif args.results.exists() and args.results.is_dir():
        # Check if this is a base directory with run-* subfolders
        args.results = find_latest_run(args.results)
    
    return args


def generate_markdown_report(all_failures: list[dict], total_tests: int, total_failures: int, 
                              openapi_methods: dict, include_llm: bool = False) -> str:
    """
    Generate a complete markdown report.
    Returns the report as a string (for CI output to GITHUB_STEP_SUMMARY).
    """
    lines = []
    
    # Header
    lines.append("## 🔬 Schemathesis API Test Summary")
    lines.append("")
    
    # Summary section
    python_summary = generate_python_summary(all_failures, total_tests, total_failures, openapi_methods)
    lines.append(python_summary)
    lines.append("")
    
    # Recommendations
    lines.append("## 🔧 Recommendations")
    lines.append("")
    deterministic_recs = generate_deterministic_recommendations(all_failures, openapi_methods)
    lines.append(deterministic_recs)
    lines.append("")
    
    # LLM insights (optional)
    if include_llm:
        prompt = build_prompt(all_failures, openapi_methods)
        llm_output = run_llm(prompt)
        if llm_output:
            lines.append("### 🤖 AI Insights")
            lines.append("")
            lines.append(llm_output)
            lines.append("")
            # Add disclaimer for small model
            lines.append("> ⚠️ **Disclaimer:** AI insights are generated by a small 0.5B parameter model and may occasionally be shallow or imprecise. Always verify recommendations against actual test results.")
            lines.append("")
    
    return "\n".join(lines)


def main():
    args = parse_args()
    
    # Validate results directory
    if not args.results.exists():
        print(f"Results directory not found: {args.results}", file=sys.stderr)
        sys.exit(1)
    
    # Find XML files
    xml_files = find_junit_xml_files(args.results)
    if not xml_files:
        print(f"No JUnit XML files found in: {args.results}", file=sys.stderr)
        sys.exit(1)
    
    if not args.ci:
        print(f"Found {len(xml_files)} JUnit XML file(s) in {args.results}", file=sys.stderr)
    
    # Parse all XML files and aggregate results
    all_failures = []
    total_tests = 0
    total_failures = 0
    
    for xml_file in xml_files:
        if not args.ci:
            print(f"  Parsing: {xml_file.name}", file=sys.stderr)
        result = parse_junit_xml(xml_file)
        total_tests += result["total_tests"]
        total_failures += result["total_failures"]
        all_failures.extend(result["failures"])
    
    if not args.ci:
        print(f"\nTotal: {total_tests} tests, {total_failures} failures", file=sys.stderr)
    
    if not all_failures:
        if args.ci:
            print("## 🔬 Schemathesis API Test Summary")
            print("")
            print(f"✅ **All {total_tests} tests passed!** No failures detected.")
        else:
            print("No failures found. Nothing to summarize.")
        sys.exit(0)
    
    # Load OpenAPI spec
    openapi_spec = load_openapi_spec(args.openapi)
    openapi_methods = extract_openapi_methods(openapi_spec) if openapi_spec else {}
    
    if openapi_methods and not args.ci:
        print(f"Loaded OpenAPI spec: {len(openapi_methods)} paths", file=sys.stderr)
    
    # Generate report
    include_llm = not args.ci and not args.no_llm
    report = generate_markdown_report(all_failures, total_tests, total_failures, openapi_methods, include_llm)
    
    if args.ci:
        # CI mode: just output clean markdown
        print(report)
    else:
        # Interactive mode: add decorations
        print("\n" + "=" * 60)
        print("📊 SCHEMATHESIS RESULTS SUMMARY")
        print("=" * 60 + "\n")
        print(report)
        print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
