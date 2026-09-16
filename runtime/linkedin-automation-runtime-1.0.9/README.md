# linkedin-automation runtime

Compiled Python runtime for the `linkedin-automation-login` OpenClaw skill. Distributed
separately from the public ClawHub skill package — see that package's `SKILL.md` for how
OpenClaw locates and invokes this runtime once installed.

Contains no `.py` source — `easy_apply`/`bot_logic`/`ai_answer`/`daily_limit`/
`connect_hiring_team`/`human_utils` ship as compiled `.pyc` bytecode (blocks casual
inspection; not encryption — a determined party can decompile it). `cli.py` ships as plain
readable `.py` since it's thin orchestration with no proprietary logic.

`.pyc` bytecode is pinned to the Python version it was compiled with — see `PYTHON_VERSION`
in this folder. `install.ps1`/`install.sh` check this automatically and fail loudly on a
mismatch rather than silently misbehaving.

## Install

```
# Windows
pwsh install.ps1

# macOS / Linux
./install.sh
```

This installs `requirements.txt` (Playwright, Anthropic SDK, python-dotenv) and runs
`python -m playwright install chrome` — the automation drives a real Chrome browser via
Playwright, and this browser install step is required regardless of how the Python code
itself is packaged.

Then:
```
cp .env.example .env
# set ANTHROPIC_API_KEY at minimum — see .env.example for every other optional setting
```

## CLI

```
python cli.py login-check   # fast, no-browser: prints logged_in / needs_login
python cli.py login         # opens a real Chrome window, waits for manual login (incl. 2FA)
python cli.py verify        # fresh browser launch, confirms the feed loads
python cli.py smoke         # live smoke test: login + >=1 Easy Apply candidate found, submits nothing
python cli.py run [N] [--scan-per-page N] [--max-scan N] [--force]   # runs a real Easy Apply sprint
```

Same CLI arguments/behavior as running the original `easy_apply.py`/etc. source directly —
`run` forwards its arguments unchanged to the existing automation's argument parser.

`N` is checked against **today's** successful submissions only, not a lifetime total — running
`run 60` behaves the same on the first sprint of the day or the fifth. Pass `--force` to run
anyway even if today's target already looks reached.

## Config

See `.env.example` for the full list. `ANTHROPIC_API_KEY` is required for AI-answered
open-ended application questions (grounded in your resume) — without it, those questions
fall back to generic hardcoded defaults. Real resume/system-prompt text: recommended is
copying `data/resume.example.txt` → `data/resume.txt` and `data/system_prompt.example.txt` →
`data/system_prompt.txt` and filling them in (gitignored if this folder is under version
control — never commit real resume content). Alternatively paste directly into the
`RESUME_TEXT`/`SYSTEM_PROMPT_TEXT` env vars (e.g. an OpenClaw settings textarea with no file
access) — if you do, wrap the value in double quotes so `python-dotenv` parses the embedded
newlines correctly; an unquoted multi-line value only has its first line read. Resolution
order: env var > local file > bundled example.

## Do NOT

- Do NOT `launch_persistent_context()` on the real Chrome profile (`...\Google\Chrome\User Data`) — hangs forever, blocked by Chrome policy. This runtime always uses a dedicated automation profile (`CHROME_PROFILE_DIR`, defaults to `~/.openclaw/workspace/.playwright-profile`).
- Do NOT copy `Network\Cookies` from real Chrome into the automation profile — encryption is app-bound, Playwright clears unrecognized cookies.
- Do NOT use remote-debugging-port on the real profile — blocked by same policy.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `.pyc` fails to import / `ImportError` on startup | Python version mismatch (bytecode is version-pinned) | Check `PYTHON_VERSION` in this folder vs. `python --version`; reinstall matching Python or get a runtime build for yours |
| Redirected to login / every job "No Easy Apply" | Session expired | `python cli.py login` |
| `smoke` reports zero candidates found | LinkedIn selectors may be stale | Retry later; if persistent, this needs a runtime rebuild from the private source |
| Daily submission limit hit | LinkedIn's per-day Easy Apply cap | `run` stops cleanly and logs the reason; resume tomorrow |
