#!/usr/bin/env bash
# Installs this linkedin-automation runtime: verifies the Python version matches what the
# bytecode was compiled against (.pyc is version-pinned — see README.md), installs
# dependencies, and installs the Playwright Chrome browser this automation drives.
# Run from inside the extracted runtime folder: ./install.sh
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

expected="$(cat PYTHON_VERSION | tr -d '[:space:]')"
actual="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
if [ "$actual" != "$expected" ]; then
    echo "ERROR: Python version mismatch: this runtime's bytecode was compiled for Python $expected, but 'python3' here is $actual. .pyc bytecode is pinned to the compiling interpreter's major.minor version and will fail to import on a mismatch. Install Python $expected, or rebuild this runtime against your Python (see the private source repo's build/compile.py)." >&2
    exit 1
fi

python3 -m pip install -r requirements.txt
python3 -m playwright install chrome

echo
echo "Runtime installed at: $(pwd)"
echo "Point the OpenClaw skill at it by setting one of:"
echo "  - env var LINKEDIN_AUTOMATION_RUNTIME_DIR=$(pwd)"
echo "  - or moving/copying this folder to the skill's default search path"
echo "    (see dist/skill/SKILL.md in the ClawHub package for the exact default path)"
echo
echo "Next: cp .env.example .env and set ANTHROPIC_API_KEY, then: python3 cli.py login-check"
