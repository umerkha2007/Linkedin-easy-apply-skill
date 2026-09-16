---
name: "linkedin-automation-login"
description: "LinkedIn job-sprint automation — verify/refresh login in the dedicated Playwright profile, then run the Easy Apply automation. Use when resuming or starting a LinkedIn application sprint."
metadata:
  openclaw:
    primaryEnv: ANTHROPIC_API_KEY
    requires:
      env: [ANTHROPIC_API_KEY]
      bins: [python]
    envVars:
      - name: LINKEDIN_AUTOMATION_RUNTIME_DIR
        required: false
        description: Path to the separately installed linkedin-automation Python runtime (the folder containing cli.py). If unset, checked at the default path below.
      - name: ANTHROPIC_API_KEY
        required: true
        description: Used by the runtime to answer open-ended Easy Apply questions, grounded in your resume
      - name: CHROME_PROFILE_DIR
        required: false
        description: Persistent Chrome/Playwright profile dir (login session, cookies). Defaults to ~/.openclaw/workspace/.playwright-profile
      - name: APPLICATION_LOG_PATH
        required: false
        description: Path to the JSON application log/dedup store. Defaults to ~/.openclaw/workspace/applications/application-log.json
      - name: SEARCH_QUERIES
        required: false
        description: Comma-separated LinkedIn search queries to rotate through
      - name: SEARCH_LOCATION
        required: false
        description: LinkedIn location filter (e.g. "United States", "Canada", "Remote")
      - name: SEARCH_TIME_RANGE
        required: false
        description: LinkedIn "date posted" filter — "day", "week" (default), or "month"
      - name: BANNED_COMPANIES
        required: false
        description: Comma-separated company names to never apply to
      - name: AUTO_CONNECT_HIRING_TEAM
        required: false
        description: Set to "false" to skip sending connection requests to the hiring team after a successful submission
      - name: RESUME_TEXT
        required: false
        description: Full resume text, pasted directly. Falls back to a generic bundled example if unset.
      - name: SYSTEM_PROMPT_TEXT
        required: false
        description: Full custom instructions for the runtime's answer-generation step (how it should phrase Easy Apply answers), pasted directly in place of the default template.
---

# LinkedIn Automation: Login + Easy Apply

## What this does

Automates a LinkedIn Easy Apply job-application sprint end to end: verifies (or refreshes)
login in a dedicated Playwright/Chrome profile, searches LinkedIn by your criteria, fills
and submits Easy Apply forms — answering open-ended questions with an LLM grounded in your
resume — logs every outcome so re-runs never double-apply, and optionally sends connection
requests to each job's hiring team after a successful submission.

## When to use this skill

Use it whenever the user asks to resume, start, or check status of a LinkedIn application
sprint, or to verify/refresh the automation's LinkedIn login. Do not attempt to reimplement
this workflow (browser automation, selector logic, application dedup, daily-limit
detection) yourself — always invoke the installed runtime described below. This skill's
package intentionally ships no implementation code; the working automation lives in a
separately installed Python runtime, and reproducing its logic ad hoc will not match its
tested behavior (dedup rules, retry rules, daily-limit handling, etc.).

## Locating the installed runtime

This skill's package (`{baseDir}`) contains no automation code — only this file and
`{baseDir}/references/README.md`. The actual automation is a separately distributed Python
runtime, set up ahead of time by the user via the steps in that reference file. Locate it
in this order:

1. `$LINKEDIN_AUTOMATION_RUNTIME_DIR`, if set.
2. The default path: `~/.openclaw/workspace/linkedin-automation-runtime/`.

If a runtime exists at either location (a `cli.py` file present there), use it directly.

If no runtime is found at either location, **stop and tell the user**. Point them at
`{baseDir}/references/README.md` for setup, and at `LINKEDIN_AUTOMATION_RUNTIME_DIR` to
tell this skill where they put it (or leave it at the default path above). Do not
substitute your own approach for locating, obtaining, or standing up the runtime — this
skill only ever drives an already-prepared installation.

Once located, every command below is: `python "<runtime_dir>/cli.py" <subcommand> [args]`.

## Inputs

All inputs are environment variables — see the `envVars` list in this file's frontmatter
for the full set. `ANTHROPIC_API_KEY` is required; everything else has a working default.

## Invoking the runtime

1. **Check login (fast, no browser):**
   `python "<runtime_dir>/cli.py" login-check`
   Output: prints exactly `logged_in` or `needs_login` on stdout.

2. **If `needs_login`, log in interactively:**
   `python "<runtime_dir>/cli.py" login`
   Opens a real Chrome window on the automation profile and waits (up to 5 minutes) for
   the user to finish logging in (including 2FA). Tell the user the window is open and
   wait for the process to exit — do not poll or interrupt it.

3. **Verify:**
   `python "<runtime_dir>/cli.py" verify`
   Output: prints `verified` on success, or `not_verified url=... title=...` on failure.

4. **Smoke test (real browser, submits nothing):**
   `python "<runtime_dir>/cli.py" smoke`
   Run before trusting a real sprint. Prints progress lines ending in either
   `SMOKE TEST PASSED — ...` or an `AssertionError` describing what failed (not logged in,
   or the scraper found zero candidates).

5. **Run a sprint:**
   `python "<runtime_dir>/cli.py" run [N] [--scan-per-page N] [--max-scan N]`
   `N` is the number of applications to submit this call (default 1). Invoke once per
   call — this automation schedules itself externally at randomized intervals and must
   not be looped internally, to avoid LinkedIn bot-detection.

## Output format

Every subcommand prints human-readable progress lines to stdout and exits 0 on success,
non-zero on failure (an unhandled exception, or an `AssertionError` from `smoke`). There is
no structured JSON output — read the printed lines directly. `run` additionally persists
every outcome (submitted / skipped / already-applied / blocked) to the JSON log at
`$APPLICATION_LOG_PATH`, which downstream tooling can read for a structured summary.

## Handling failures

- Non-zero exit + login-related text (`NOT LOGGED IN`, redirected to `/login`) → session
  expired; run `login` again, then retry.
- `smoke` fails with zero candidates found → possible stale LinkedIn selectors on the
  runtime's end; this needs a runtime rebuild/update, not a workaround here — report it to
  the user rather than trying to patch around it.
- `run` stops cleanly citing a daily submission limit → expected LinkedIn behavior, not an
  error; tell the user to resume tomorrow.
- Any other non-zero exit → surface the printed error text to the user verbatim; do not
  guess at a fix or attempt to edit the runtime.
