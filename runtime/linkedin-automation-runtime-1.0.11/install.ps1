# Installs this linkedin-automation runtime: verifies the Python version matches what the
# bytecode was compiled against (.pyc is version-pinned — see README.md), installs
# dependencies, and installs the Playwright Chrome browser this automation drives.
# Run from inside the extracted runtime folder:
#   pwsh install.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$expected = (Get-Content PYTHON_VERSION).Trim()
$actual = (python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')").Trim()
if ($actual -ne $expected) {
    Write-Error "Python version mismatch: this runtime's bytecode was compiled for Python $expected, but 'python' here is $actual. .pyc bytecode is pinned to the compiling interpreter's major.minor version and will fail to import on a mismatch. Install Python $expected, or rebuild this runtime against your Python (see the private source repo's build/compile.py)."
}

python -m pip install -r requirements.txt
python -m playwright install chrome

Write-Host "`nRuntime installed at: $root"
Write-Host "Point the OpenClaw skill at it by setting one of:"
Write-Host "  - env var LINKEDIN_AUTOMATION_RUNTIME_DIR = $root"
Write-Host "  - or moving/copying this folder to the skill's default search path"
Write-Host "    (see dist/skill/SKILL.md in the ClawHub package for the exact default path)"
Write-Host "`nNext: cp .env.example .env and set ANTHROPIC_API_KEY, then: python cli.py login-check"
