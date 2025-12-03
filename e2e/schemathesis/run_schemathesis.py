#!/usr/bin/env python3
"""
Schemathesis API Testing Script with Authentication

This script:
1. Reads configuration from .env file (in e2e/ or via environment variables)
2. Authenticates via API to get a token
3. Runs Schemathesis tests with the token
4. Generates Allure-compatible JUnit results

Usage:
    # From schemathesis/ folder with virtual env activated:
    python run_schemathesis.py

    # Or specify custom OpenAPI file:
    OPENAPI_FILE=custom-api.json python run_schemathesis.py
"""

import os
import sys
import subprocess
import requests
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

# Paths relative to this script (e2e/schemathesis/)
SCRIPT_DIR = Path(__file__).parent.resolve()  # e2e/schemathesis/
E2E_DIR = SCRIPT_DIR.parent                    # e2e/
PROJECT_ROOT = E2E_DIR.parent                  # NoteTaker/

# Default file locations
DEFAULT_OPENAPI_FILE = E2E_DIR / "openapi.json"
RESULTS_DIR = SCRIPT_DIR / "allure-results"
REPORT_DIR = SCRIPT_DIR / "allure-report"


# ═══════════════════════════════════════════════════════════════════════════════
# ENVIRONMENT LOADING
# ═══════════════════════════════════════════════════════════════════════════════

def get_env_file() -> Path:
    """
    Select the correct .env file based on ENV variable.
    Matches Playwright config behavior:
      - ENV=prod  → .env.prod
      - ENV=dev   → .env.dev
      - Otherwise → .env (local)
    """
    env_name = os.getenv("ENV", "local").lower()
    
    if env_name == "prod":
        env_file = E2E_DIR / ".env.prod"
    elif env_name == "dev":
        env_file = E2E_DIR / ".env.dev"
    else:
        env_file = E2E_DIR / ".env"
    
    print(f"🌍 Environment: {env_name}")
    return env_file


def load_env(env_file: Path = None) -> dict:
    """Load environment variables from .env file."""
    if env_file is None:
        env_file = get_env_file()
    
    env_vars = {}
    
    if not env_file.exists():
        print(f"⚠️  Warning: {env_file} not found, using system environment variables")
        return env_vars
    
    print(f"📄 Loading environment from: {env_file}")
    
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip()
    
    return env_vars


# ═══════════════════════════════════════════════════════════════════════════════
# AUTHENTICATION
# ═══════════════════════════════════════════════════════════════════════════════

def get_auth_token(base_url: str, email: str, password: str) -> str:
    """
    Authenticate via API and return the auth token.
    POST /users/login with form data.
    Returns x-auth-token for subsequent requests.
    """
    login_url = f"{base_url}/users/login"
    
    print(f"🔐 Authenticating at: {login_url}")
    
    try:
        response = requests.post(
            login_url,
            data={"email": email, "password": password},
            timeout=30
        )
    except requests.RequestException as e:
        print(f"❌ Connection error: {e}")
        sys.exit(1)
    
    if response.status_code != 200:
        print(f"❌ Login failed with status {response.status_code}: {response.text}")
        sys.exit(1)
    
    data = response.json()
    
    if not data.get("success"):
        print(f"❌ Login failed: {data.get('message', 'Unknown error')}")
        sys.exit(1)
    
    token = data.get("data", {}).get("token")
    
    if not token:
        print("❌ No token received from login response")
        sys.exit(1)
    
    print("✅ Authentication successful")
    return token


# ═══════════════════════════════════════════════════════════════════════════════
# SCHEMATHESIS EXECUTION
# ═══════════════════════════════════════════════════════════════════════════════

def run_schemathesis(
    openapi_file: Path,
    base_url: str,
    auth_token: str,
    results_dir: Path = RESULTS_DIR,
    max_examples: int = 50,
    extra_args: list = None
) -> int:
    """
    Run Schemathesis with authentication header and JUnit reporting.
    
    Args:
        openapi_file: Path to OpenAPI spec file
        base_url: API base URL
        auth_token: x-auth-token for authentication
        results_dir: Directory for JUnit XML output
        max_examples: Maximum test cases per endpoint
        extra_args: Additional Schemathesis CLI arguments
    
    Returns:
        Exit code from Schemathesis
    """
    # Clean previous results
    if results_dir.exists():
        import shutil
        shutil.rmtree(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Build Schemathesis command
    cmd = [
        "schemathesis", "run",
        str(openapi_file),
        "-u", base_url,
        "-H", f"x-auth-token:{auth_token}",
        "--report", "junit",
        "--report-dir", str(results_dir),
        "--checks", "all",
        "-n", str(max_examples),
        "--continue-on-failure",
    ]
    
    # Add any extra arguments
    if extra_args:
        cmd.extend(extra_args)
    
    print(f"\n🧪 Running Schemathesis...")
    print(f"   OpenAPI:     {openapi_file}")
    print(f"   Base URL:    {base_url}")
    print(f"   Results:     {results_dir}")
    print(f"   Max Examples: {max_examples}")
    print(f"\n   Command: {' '.join(cmd)}\n")
    print("=" * 70)
    
    # Set environment for subprocess
    env = os.environ.copy()
    env["ALLURE_RESULTS_DIR"] = str(results_dir)
    
    result = subprocess.run(cmd, env=env)
    
    print("=" * 70)
    return result.returncode


def list_results(results_dir: Path = RESULTS_DIR):
    """List generated result files."""
    if not results_dir.exists():
        print(f"\n⚠️  No results directory found at {results_dir}")
        return
    
    files = list(results_dir.iterdir())
    if not files:
        print(f"\n⚠️  Results directory is empty: {results_dir}")
        return
    
    print(f"\n📁 Results in {results_dir}:")
    for f in files:
        size = f.stat().st_size
        print(f"   - {f.name} ({size:,} bytes)")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 70)
    print("🔬 Schemathesis API Fuzz Testing with Authentication")
    print("=" * 70)
    
    # Load configuration from e2e/.env
    env_vars = load_env()
    
    # Get configuration (env file takes precedence, then system env)
    base_url = env_vars.get("API_URL") or os.getenv("API_URL")
    email = env_vars.get("EMAIL") or os.getenv("EMAIL")
    password = env_vars.get("PASSWORD") or os.getenv("PASSWORD")
    
    # OpenAPI file - check env, then use default
    openapi_env = env_vars.get("OPENAPI_FILE") or os.getenv("OPENAPI_FILE")
    if openapi_env:
        openapi_file = Path(openapi_env)
        if not openapi_file.is_absolute():
            openapi_file = E2E_DIR / openapi_env
    else:
        openapi_file = DEFAULT_OPENAPI_FILE
    
    # Max examples per endpoint
    max_examples = int(
        env_vars.get("SCHEMATHESIS_MAX_EXAMPLES") or 
        os.getenv("SCHEMATHESIS_MAX_EXAMPLES") or 
        "50"
    )
    
    # Validate required config
    errors = []
    if not base_url:
        errors.append("API_URL not set")
    if not email:
        errors.append("EMAIL not set")
    if not password:
        errors.append("PASSWORD not set")
    if not openapi_file.exists():
        errors.append(f"OpenAPI file not found: {openapi_file}")
    
    if errors:
        print("\n❌ Configuration errors:")
        for err in errors:
            print(f"   - {err}")
        print("\nPlease set these in e2e/.env or as environment variables.")
        sys.exit(1)
    
    print(f"\n📋 Configuration:")
    print(f"   Base URL:    {base_url}")
    print(f"   Email:       {email}")
    print(f"   OpenAPI:     {openapi_file}")
    print(f"   Results Dir: {RESULTS_DIR}")
    
    # Authenticate
    token = get_auth_token(base_url, email, password)
    
    # Run Schemathesis
    exit_code = run_schemathesis(
        openapi_file=openapi_file,
        base_url=base_url,
        auth_token=token,
        results_dir=RESULTS_DIR,
        max_examples=max_examples
    )
    
    # Show results
    list_results()
    
    # Summary
    print("\n" + "=" * 70)
    if exit_code == 0:
        print("✅ Schemathesis tests completed successfully")
    else:
        print(f"⚠️  Schemathesis tests completed with exit code {exit_code}")
        print("   (Non-zero exit code indicates API issues were found)")
    print("=" * 70)
    
    print(f"\n💡 Next steps:")
    print(f"   Generate Allure report: allure generate {RESULTS_DIR} -o {REPORT_DIR} --clean")
    print(f"   View Allure report:     allure open {REPORT_DIR}")
    print(f"   Or serve directly:      allure serve {RESULTS_DIR}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
