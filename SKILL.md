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
      - name: ANTHROPIC_API_KEY
        required: true
        description: Used to answer open-ended Easy Apply questions, grounded in dist/lib/data/resume.txt
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
        description: LinkedIn "date posted" filter — "day" (past 24 hours), "week" (past week, default), or "month" (past month)
      - name: BANNED_COMPANIES
        required: false
        description: Comma-separated company names to never apply to
      - name: POSTAL_CODE
        required: false
        description: Postal/zip code used to fill address form fields
      - name: SALARY_EXPECTATION
        required: false
        description: Expected salary figure used to fill compensation form fields
      - name: AUTO_CONNECT_HIRING_TEAM
        required: false
        description: Set to "false" to skip sending connection requests to the hiring team after a successful submission
      - name: CANDIDATE_NAME
        required: false
        description: Candidate's full name, injected into the system prompt for AI-answered questions
      - name: CANDIDATE_TITLE
        required: false
        description: Candidate's professional title, e.g. "Senior Full Stack Developer"
      - name: CANDIDATE_LOCATION
        required: false
        description: Candidate's current location, e.g. "Toronto, Ontario, Canada"
      - name: WORK_AUTHORIZATION
        required: false
        description: Candidate's work authorization status, e.g. "Canadian Citizen, authorized to work without sponsorship"
      - name: YEARS_EXPERIENCE
        required: false
        description: Candidate's years of professional experience
      - name: NOTICE_PERIOD_DAYS
        required: false
        description: Notice period in days used when answering availability questions
      - name: SALARY_RANGE
        required: false
        description: Salary range string used when answering compensation questions, e.g. "$150,000-$170,000 CAD annually"
      - name: RESUME_TEXT
        required: false
        description: Full resume text, pasted directly (multi-line). Overrides dist/lib/data/resume.txt. Falls back to a generic bundled example if left unset.
      - name: SYSTEM_PROMPT_TEXT
        required: false
        description: Full custom system prompt, pasted directly (multi-line), overriding the bundled template entirely. Falls back to dist/lib/data/system_prompt.txt, then the bundled example built from the CANDIDATE_*/WORK_AUTHORIZATION/etc. vars above.
---

# LinkedIn Automation: Login + Easy Apply

This skill drives a compiled automation core (`dist/lib/*.pyc`) via a small CLI. The
implementation isn't published here — only the interface below.

## Do NOT

- Do NOT `launch_persistent_context()` on the real Chrome profile (`...\Google\Chrome\User Data`) — hangs forever, blocked by Chrome policy.
- Do NOT copy `Network\Cookies` from real Chrome into the automation profile — encryption is app-bound, Playwright clears unrecognized cookies.
- Do NOT use remote-debugging-port on the real profile — blocked by same policy.

## Step 1: One-time setup

```
cd <skill install dir>
python -m pip install -r requirements.txt
python -m playwright install chrome
```

For AI-answered application questions (recommended — without it, open-ended questions get generic hardcoded defaults):
1. Copy `.env.example` → `.env`, set `ANTHROPIC_API_KEY` (https://console.anthropic.com/settings/keys). **Required even inside Claude Code** — this runs as a standalone process with no access to Claude Code's own credentials.
2. Every other setting has a working default (see the `envVars` list above) — the bot runs out of the box with generic placeholder resume/persona content. To personalize, set whichever of these you want, in any combination:
   - **Paste directly into config** (fastest — works as an OpenClaw settings textarea): `RESUME_TEXT` with your real resume, and either the `CANDIDATE_NAME`/`CANDIDATE_LOCATION`/`WORK_AUTHORIZATION`/etc. persona vars (filled into the bundled template) or a full custom `SYSTEM_PROMPT_TEXT`.
   - **Or edit local files** (if you'd rather keep long text out of `.env`): copy `dist/lib/data/resume.example.txt` → `dist/lib/data/resume.txt` and `dist/lib/data/system_prompt.example.txt` → `dist/lib/data/system_prompt.txt`, then fill them in. Both are gitignored — they never get committed.
   - Resolution order for each: env var > local file > bundled example — so partial setup (e.g. only `RESUME_TEXT` set) still works.

## Step 2: Login (automation profile: `$CHROME_PROFILE_DIR`, defaults to `~/.openclaw/workspace/.playwright-profile`)

1. **Check session (fast, no browser):**
   ```
   python dist\lib\cli.pyc login-check
   ```
   Prints `logged_in` or `needs_login`.
   - **Exception — file locked:** close Chrome first (`taskkill //IM chrome.exe //F`), then delete `SingletonLock`/`SingletonCookie`/`SingletonSocket` from the profile dir before retrying.

2. **If `needs_login`**, open the profile for a manual login (never plain Chrome, never the real profile):
   ```
   python dist\lib\cli.pyc login
   ```
   Opens a real Chrome window on the automation profile and waits (up to 5 minutes) for you to
   finish logging in (including 2FA). Tell the user the browser window is open, then wait for the
   process to finish — do not poll.

3. **Verify:**
   ```
   python dist\lib\cli.pyc verify
   ```
   Prints `verified` on success.

## Step 3: Live smoke test (real browser, no submissions)

```
python dist\lib\cli.pyc smoke
```

Confirms login is valid and the scraper finds ≥1 Easy Apply candidate. Run before trusting a real
sprint, and whenever a sprint reports zero candidates found (possible sign of a stale LinkedIn
selector on the automation's end).

## Step 4: Run Easy Apply

```
python dist\lib\cli.pyc run
```

Optional args (same positions/flags as before): `run <target>` `--scan-per-page N` `--max-scan N`.

- Live-searches LinkedIn (`SEARCH_QUERIES`/`SEARCH_LOCATION`/`SEARCH_TIME_RANGE` env vars, Easy Apply filter), random batch size (2-5), randomized delays (~4-9s between applications). Invoke once per call — schedule externally at random intervals, don't loop internally, to avoid bot-detection.
- Logs every outcome to `$APPLICATION_LOG_PATH` (default `~/.openclaw/workspace/applications/application-log.json`), deduped by company + URL.
- Respects `BANNED_COMPANIES` (env var, comma-separated).
- `AUTO_CONNECT_HIRING_TEAM` (env var, default `true`) sends connection requests to hiring-team members after a successful submission.

## Exception handling reference

| Symptom | Likely cause | Fix |
|---|---|---|
| Redirected to login / every job "No Easy Apply" | Session expired | Re-run Step 2 |
| `smoke` reports zero candidates found | Underlying scraper selectors may be stale on LinkedIn's end | Retry later; if persistent, file an issue against this skill |
| Daily submission limit hit | LinkedIn's per-day Easy Apply cap | `run` stops cleanly and logs the reason; resume tomorrow |
| Company permanently skipped | Only successful/already-applied entries are terminal — blocked/skipped rows are retried automatically on the next `run` | No action needed |
