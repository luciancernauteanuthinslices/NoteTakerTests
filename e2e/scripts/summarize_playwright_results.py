#!/usr/bin/env python3
"""
Summarize Playwright Allure JSON results using a local LLM (llama.cpp).

Usage:
    python summarize_playwright_results.py [path/to/allure-results]

If no path is given, defaults to ../allure-results/
"""

import sys
import os
import glob
import re
import json
import argparse
from pathlib import Path
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════════

MODEL_PATH = "/Users/lucian.cernauteanuthinslices.com/Documents/LLM Models/Qwen2.5-0.5B-Instruct-Q4_0.gguf"

# Default paths (relative to this script)
SCRIPT_DIR = Path(__file__).parent.resolve()
DEFAULT_RESULTS_DIR = SCRIPT_DIR.parent / "allure-results"

# LLM settings - tuned for concise, non-repetitive output
N_CTX = 4096          # Context window (smaller for Playwright - less data)
MAX_TOKENS = 300      # Max output tokens
TEMPERATURE = 0.15    # Low for deterministic output
REPEAT_PENALTY = 1.3  # Penalty to prevent repetition
TOP_P = 0.9           # Nucleus sampling for diversity
TOP_K = 40            # Top-k sampling

# Status icons (Allure-style)
STATUS_ICONS = {
    "passed": "✅",
    "failed": "❌",
    "broken": "💔",
    "skipped": "⏭️",
    "unknown": "❓",
}

# Status colors for markdown (GitHub compatible)
STATUS_LABELS = {
    "passed": "🟢 Passed",
    "failed": "🔴 Failed",
    "broken": "🟠 Broken",
    "skipped": "⚪ Skipped",
    "unknown": "❓ Unknown",
}


# ═══════════════════════════════════════════════════════════════════════════════
# Step 1: Parse Allure JSON results
# ═══════════════════════════════════════════════════════════════════════════════

def find_result_files(results_dir: Path) -> list[Path]:
    """Find all Allure result JSON files in the given directory."""
    pattern = str(results_dir / "*-result.json")
    files = glob.glob(pattern)
    return [Path(f) for f in sorted(files)]


def parse_result_file(json_path: Path) -> dict:
    """
    Parse a single Allure result JSON file.
    
    Returns:
        {
            "name": str,
            "fullName": str,
            "status": str,
            "duration_ms": int,
            "suite": str,
            "file": str,
            "error": str or None,
            "steps_count": int,
        }
    """
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Extract basic info
    name = data.get("name", "Unknown test")
    full_name = data.get("fullName", name)
    status = data.get("status", "unknown")
    
    # Calculate duration
    start = data.get("start", 0)
    stop = data.get("stop", 0)
    duration_ms = stop - start if stop > start else 0
    
    # Extract suite/file from labels
    labels = {l.get("name"): l.get("value") for l in data.get("labels", [])}
    suite = labels.get("parentSuite", labels.get("suite", ""))
    file = labels.get("package", "")
    
    # Extract error message if failed
    error = None
    status_details = data.get("statusDetails", {})
    if status in ("failed", "broken"):
        error = status_details.get("message", "")
        if not error:
            error = status_details.get("trace", "")[:500]  # Truncate long traces
    
    # Count steps
    def count_steps(steps_list):
        count = len(steps_list)
        for step in steps_list:
            count += count_steps(step.get("steps", []))
        return count
    
    steps_count = count_steps(data.get("steps", []))
    
    return {
        "name": name,
        "fullName": full_name,
        "status": status,
        "duration_ms": duration_ms,
        "suite": suite,
        "file": file,
        "error": error,
        "steps_count": steps_count,
    }


def parse_environment(results_dir: Path) -> dict:
    """Parse environment.properties file if it exists."""
    env_file = results_dir / "environment.properties"
    env = {}
    
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line:
                    key, value = line.split('=', 1)
                    env[key.strip()] = value.strip()
    
    return env


def aggregate_results(results: list[dict]) -> dict:
    """
    Aggregate test results into summary statistics.
    
    Returns:
        {
            "total": int,
            "passed": int,
            "failed": int,
            "broken": int,
            "skipped": int,
            "pass_rate": float,
            "total_duration_ms": int,
            "avg_duration_ms": int,
            "suites": {suite_name: {"passed": N, "failed": N, ...}},
            "failures": [{"name": ..., "error": ..., "file": ...}],
            "slowest": [{"name": ..., "duration_ms": ...}],
        }
    """
    stats = {
        "total": len(results),
        "passed": 0,
        "failed": 0,
        "broken": 0,
        "skipped": 0,
        "unknown": 0,
        "total_duration_ms": 0,
        "suites": {},
        "failures": [],
        "slowest": [],
    }
    
    for r in results:
        status = r["status"]
        stats[status] = stats.get(status, 0) + 1
        stats["total_duration_ms"] += r["duration_ms"]
        
        # Group by suite
        suite = r["suite"] or "Default"
        if suite not in stats["suites"]:
            stats["suites"][suite] = {"passed": 0, "failed": 0, "broken": 0, "skipped": 0}
        if status in stats["suites"][suite]:
            stats["suites"][suite][status] += 1
        
        # Collect failures
        if status in ("failed", "broken"):
            stats["failures"].append({
                "name": r["name"],
                "file": r["file"],
                "error": r["error"],
                "status": status,
            })
    
    # Calculate metrics
    stats["pass_rate"] = (stats["passed"] / stats["total"] * 100) if stats["total"] > 0 else 0
    stats["avg_duration_ms"] = stats["total_duration_ms"] // stats["total"] if stats["total"] > 0 else 0
    
    # Find slowest tests
    sorted_by_duration = sorted(results, key=lambda x: x["duration_ms"], reverse=True)
    stats["slowest"] = [
        {"name": r["name"], "duration_ms": r["duration_ms"], "file": r["file"]}
        for r in sorted_by_duration[:5]
    ]
    
    return stats


# ═══════════════════════════════════════════════════════════════════════════════
# Step 2: Generate deterministic report (no LLM needed)
# ═══════════════════════════════════════════════════════════════════════════════

def format_duration(ms: int) -> str:
    """Format milliseconds to human-readable string."""
    if ms < 1000:
        return f"{ms}ms"
    elif ms < 60000:
        return f"{ms / 1000:.1f}s"
    else:
        minutes = ms // 60000
        seconds = (ms % 60000) / 1000
        return f"{minutes}m {seconds:.0f}s"


def generate_summary_report(stats: dict, env: dict) -> str:
    """Generate the main summary section."""
    lines = []
    
    # Overall status badge
    if stats["failed"] > 0 or stats["broken"] > 0:
        overall = "❌ **TESTS FAILED**"
    elif stats["skipped"] > 0 and stats["passed"] == 0:
        overall = "⏭️ **ALL TESTS SKIPPED**"
    elif stats["passed"] > 0 and stats["failed"] == 0 and stats["broken"] == 0:
        if stats["skipped"] > 0:
            overall = "✅ **TESTS PASSED** (some skipped)"
        else:
            overall = "✅ **ALL TESTS PASSED**"
    else:
        overall = "⚠️ **TESTS COMPLETED WITH ISSUES**"
    
    lines.append(f"### {overall}")
    lines.append("")
    
    # Stats table
    lines.append("| Status | Count | Percentage |")
    lines.append("|--------|-------|------------|")
    
    for status in ["passed", "failed", "broken", "skipped"]:
        count = stats.get(status, 0)
        if count > 0 or status in ("passed", "failed"):
            pct = (count / stats["total"] * 100) if stats["total"] > 0 else 0
            icon = STATUS_ICONS.get(status, "")
            lines.append(f"| {icon} {status.capitalize()} | {count} | {pct:.1f}% |")
    
    lines.append(f"| **Total** | **{stats['total']}** | **100%** |")
    lines.append("")
    
    # Metrics
    lines.append("### ⏱️ Performance Metrics")
    lines.append("")
    lines.append(f"- **Total Duration:** {format_duration(stats['total_duration_ms'])}")
    lines.append(f"- **Average Test Duration:** {format_duration(stats['avg_duration_ms'])}")
    lines.append(f"- **Pass Rate:** {stats['pass_rate']:.1f}%")
    lines.append("")
    
    # Environment info
    if env:
        lines.append("### 🌍 Environment")
        lines.append("")
        lines.append("| Property | Value |")
        lines.append("|----------|-------|")
        for key, value in env.items():
            # Truncate long values
            display_value = value[:50] + "..." if len(value) > 50 else value
            lines.append(f"| {key} | `{display_value}` |")
        lines.append("")
    
    return "\n".join(lines)


def generate_failures_section(failures: list[dict]) -> str:
    """Generate the failures section with details."""
    if not failures:
        return ""
    
    lines = []
    lines.append("### ❌ Failed Tests")
    lines.append("")
    
    for i, f in enumerate(failures[:10], 1):  # Limit to 10 failures
        icon = STATUS_ICONS.get(f["status"], "❌")
        lines.append(f"**{i}. {icon} {f['name']}**")
        lines.append(f"- 📁 File: `{f['file']}`")
        if f["error"]:
            # Clean and truncate error message
            error = f["error"].replace('\n', ' ').strip()[:200]
            lines.append(f"- 💬 Error: {error}")
        lines.append("")
    
    if len(failures) > 10:
        lines.append(f"*... and {len(failures) - 10} more failures*")
        lines.append("")
    
    return "\n".join(lines)


def generate_suites_section(suites: dict) -> str:
    """Generate the suites breakdown section."""
    if not suites or len(suites) <= 1:
        return ""
    
    lines = []
    lines.append("### 📦 Test Suites")
    lines.append("")
    lines.append("| Suite | ✅ | ❌ | 💔 | ⏭️ |")
    lines.append("|-------|-----|-----|-----|-----|")
    
    for suite, counts in sorted(suites.items()):
        lines.append(
            f"| {suite} | {counts.get('passed', 0)} | {counts.get('failed', 0)} | "
            f"{counts.get('broken', 0)} | {counts.get('skipped', 0)} |"
        )
    
    lines.append("")
    return "\n".join(lines)


def generate_slowest_section(slowest: list[dict]) -> str:
    """Generate the slowest tests section."""
    if not slowest:
        return ""
    
    lines = []
    lines.append("### 🐢 Slowest Tests")
    lines.append("")
    lines.append("| Test | Duration | File |")
    lines.append("|------|----------|------|")
    
    for t in slowest:
        duration = format_duration(t["duration_ms"])
        lines.append(f"| {t['name']} | {duration} | `{t['file']}` |")
    
    lines.append("")
    return "\n".join(lines)


def generate_deterministic_recommendations(stats: dict) -> str:
    """Generate actionable recommendations based on test results."""
    recommendations = []
    
    # Failure-based recommendations
    if stats["failed"] > 0:
        recommendations.append(
            f"Investigate and fix the {stats['failed']} failing test(s) before merging."
        )
    
    if stats["broken"] > 0:
        recommendations.append(
            f"Review {stats['broken']} broken test(s) - these may indicate infrastructure or setup issues."
        )
    
    # Skip-based recommendations
    if stats["skipped"] > 0:
        skip_pct = stats["skipped"] / stats["total"] * 100
        if skip_pct > 20:
            recommendations.append(
                f"High skip rate ({skip_pct:.0f}%) - review if skipped tests should be enabled or removed."
            )
        else:
            recommendations.append(
                f"Review {stats['skipped']} skipped test(s) to ensure they are intentionally disabled."
            )
    
    # Performance recommendations
    if stats["avg_duration_ms"] > 10000:  # > 10 seconds average
        recommendations.append(
            f"Average test duration is {format_duration(stats['avg_duration_ms'])} - consider parallelization or optimization."
        )
    
    # Pass rate recommendations
    if stats["pass_rate"] < 80 and stats["total"] > 5:
        recommendations.append(
            f"Pass rate is {stats['pass_rate']:.0f}% - prioritize test stability before adding new tests."
        )
    elif stats["pass_rate"] == 100:
        recommendations.append(
            "All tests passing - consider adding more edge case coverage."
        )
    
    # Suite-based recommendations
    failing_suites = [
        suite for suite, counts in stats["suites"].items()
        if counts.get("failed", 0) > 0 or counts.get("broken", 0) > 0
    ]
    if len(failing_suites) > 1:
        recommendations.append(
            f"Multiple suites have failures ({', '.join(failing_suites[:3])}) - check for shared dependencies."
        )
    
    if not recommendations:
        recommendations.append("Test suite is healthy - continue monitoring for regressions.")
    
    # Format as numbered list
    return "\n".join(f"{i+1}. {rec}" for i, rec in enumerate(recommendations[:8]))


# ═══════════════════════════════════════════════════════════════════════════════
# Step 3: Run the LLM (optional)
# ═══════════════════════════════════════════════════════════════════════════════

SYSTEM_PROMPT = """You are a QA engineer analyzing Playwright test results.

Generate 3-5 brief, actionable insights based on the test data below.

Rules:
- Output only a numbered list (1., 2., 3., ...).
- Each item must be one sentence.
- Focus on patterns, root causes, and next steps.
- Be specific - mention test names or suites when relevant.
- No repetition, no fluff, no greetings."""


def build_llm_prompt(stats: dict, failures: list[dict]) -> str:
    """Build a concise prompt for the LLM."""
    # Summarize key data points
    summary = f"Tests: {stats['total']} total, {stats['passed']} passed, {stats['failed']} failed, {stats['skipped']} skipped."
    summary += f" Pass rate: {stats['pass_rate']:.0f}%."
    summary += f" Duration: {format_duration(stats['total_duration_ms'])}."
    
    # Add failure info
    if failures:
        failure_names = [f["name"] for f in failures[:5]]
        summary += f" Failed tests: {', '.join(failure_names)}."
    
    # Add suite info
    failing_suites = [s for s, c in stats["suites"].items() if c.get("failed", 0) > 0]
    if failing_suites:
        summary += f" Failing suites: {', '.join(failing_suites[:3])}."
    
    return f"""{SYSTEM_PROMPT}

Data: {summary}

Insights:"""


def run_llm(prompt: str) -> str:
    """Load the model and generate insights."""
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
    
    print("Generating insights...", file=sys.stderr)
    output = llm(
        prompt,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
        repeat_penalty=REPEAT_PENALTY,
        top_p=TOP_P,
        top_k=TOP_K,
        stop=["===", "---", "Data:", "\n\n\n"],
    )
    
    raw_text = output["choices"][0]["text"].strip()
    return post_process_output(raw_text)


def post_process_output(text: str) -> str:
    """Clean up LLM output."""
    lines = text.split('\n')
    result_lines = []
    insight_count = 0
    
    for line in lines:
        stripped = line.strip()
        
        # Skip empty or echo lines
        if not stripped or stripped.startswith('Data:'):
            continue
        
        # Check if this is a numbered insight
        if re.match(r'^\d+\.', stripped):
            insight_count += 1
            if insight_count <= 5:
                result_lines.append(line)
            else:
                break
    
    return '\n'.join(result_lines).strip()


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Summarize Playwright Allure JSON results",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Local run with LLM:
  python summarize_playwright_results.py
  
  # CI mode (no LLM, clean markdown output):
  python summarize_playwright_results.py --ci
  
  # Custom path:
  python summarize_playwright_results.py --results ./allure-results
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
        default=DEFAULT_RESULTS_DIR,
        help=f"Path to allure-results directory (default: {DEFAULT_RESULTS_DIR})"
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Skip LLM insights (use deterministic only)"
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Compact output (skip suites and slowest sections)"
    )
    
    # Support legacy positional argument
    parser.add_argument("legacy_results", nargs="?", type=Path, help=argparse.SUPPRESS)
    
    args = parser.parse_args()
    
    if args.legacy_results:
        args.results = args.legacy_results
    
    return args


def generate_markdown_report(stats: dict, env: dict, include_llm: bool = False, compact: bool = False) -> str:
    """Generate a complete markdown report."""
    lines = []
    
    # Header
    lines.append("## 🎭 Playwright E2E Test Summary")
    lines.append("")
    
    # Main summary
    lines.append(generate_summary_report(stats, env))
    
    # Failures (always show if present)
    if stats["failures"]:
        lines.append(generate_failures_section(stats["failures"]))
    
    # Suites breakdown (skip in compact mode)
    if not compact:
        lines.append(generate_suites_section(stats["suites"]))
        lines.append(generate_slowest_section(stats["slowest"]))
    
    # Recommendations
    lines.append("### 💡 Recommendations")
    lines.append("")
    lines.append(generate_deterministic_recommendations(stats))
    lines.append("")
    
    # LLM insights (optional)
    if include_llm:
        prompt = build_llm_prompt(stats, stats["failures"])
        llm_output = run_llm(prompt)
        if llm_output:
            lines.append("### 🤖 AI Insights")
            lines.append("")
            lines.append(llm_output)
            lines.append("")
    
    return "\n".join(lines)


def main():
    args = parse_args()
    
    # Validate results directory
    if not args.results.exists():
        print(f"Results directory not found: {args.results}", file=sys.stderr)
        sys.exit(1)
    
    # Find result files
    result_files = find_result_files(args.results)
    if not result_files:
        if args.ci:
            print("## 🎭 Playwright E2E Test Summary")
            print("")
            print("⚠️ No test results found. Tests may not have run.")
        else:
            print(f"No result files found in: {args.results}", file=sys.stderr)
        sys.exit(0)
    
    if not args.ci:
        print(f"Found {len(result_files)} test result(s) in {args.results}", file=sys.stderr)
    
    # Parse all results
    results = []
    for rf in result_files:
        try:
            results.append(parse_result_file(rf))
        except Exception as e:
            if not args.ci:
                print(f"  Warning: Could not parse {rf.name}: {e}", file=sys.stderr)
    
    if not results:
        if args.ci:
            print("## 🎭 Playwright E2E Test Summary")
            print("")
            print("⚠️ Could not parse any test results.")
        else:
            print("No valid results to summarize.", file=sys.stderr)
        sys.exit(0)
    
    # Parse environment
    env = parse_environment(args.results)
    
    # Aggregate statistics
    stats = aggregate_results(results)
    
    if not args.ci:
        print(f"Total: {stats['total']} tests, {stats['passed']} passed, {stats['failed']} failed", file=sys.stderr)
    
    # Generate report
    include_llm = not args.ci and not args.no_llm
    report = generate_markdown_report(stats, env, include_llm, args.compact)
    
    if args.ci:
        # CI mode: just output clean markdown
        print(report)
    else:
        # Interactive mode: add decorations
        print("\n" + "=" * 60)
        print("🎭 PLAYWRIGHT TEST RESULTS SUMMARY")
        print("=" * 60 + "\n")
        print(report)
        print("=" * 60)
    
    # Exit with appropriate code
    if stats["failed"] > 0 or stats["broken"] > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
