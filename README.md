# LinkedIn Automation (OpenClaw skill)

Automates LinkedIn Easy Apply job sprints: login verification, job search, AI-answered
application questions, submission logging, and optional hiring-team connection requests.

This package contains only the OpenClaw skill definition ([SKILL.md](SKILL.md)) — no
implementation code. The automation itself runs as a separately distributed Python
runtime that you install once, outside of ClawHub.

## Setup

Install the runtime once, manually, before asking the agent to run a sprint — this skill
never downloads or executes anything itself.

1. **Download** the latest `linkedin-automation-runtime-<version>.zip` and its `.sha256`
   file from this repo's [GitHub Releases page](https://github.com/umerkha2007/Linkedin-easy-apply-skill/releases).
   Only use this page — never a mirror, forum link, or re-upload.
2. **Verify the download** (takes 10 seconds, don't skip it):
   ```
   # Windows
   Get-FileHash linkedin-automation-runtime-<version>.zip -Algorithm SHA256

   # macOS / Linux
   sha256sum linkedin-automation-runtime-<version>.zip
   ```
   The result must match **both** the `.sha256` file next to the download **and** the
   `expectedRuntimeSha256` value in this skill's `SKILL.md`. If either doesn't match, stop —
   don't extract or run the archive.
3. **Extract** the zip, then move/rename the extracted folder to:
   `~/.openclaw/workspace/linkedin-automation-runtime/`
   (On Windows that's `%USERPROFILE%\.openclaw\workspace\linkedin-automation-runtime`.)
   This is the skill's default search path, so you won't need to set any extra variables.
4. **Run the installer** from inside that folder:
   ```
   # Windows
   pwsh install.ps1

   # macOS / Linux
   ./install.sh
   ```
   This installs the runtime's Python dependencies and the Playwright Chrome browser.
5. **Configure it**: copy `.env.example` to `.env` in that same folder, then open `.env` and
   fill in at least `ANTHROPIC_API_KEY` (get one at
   https://console.anthropic.com/settings/keys). The other variables have sensible
   defaults — see the comments in `.env.example` for what each one does; only change what
   you need (e.g. `SEARCH_QUERIES`, `SEARCH_LOCATION`, `CANDIDATE_NAME`, `RESUME_TEXT`).

That's it — the runtime is ready. You do not need to hash `cli.py` yourself; the agent
re-verifies it automatically against a value pinned in this skill's own `SKILL.md` before
every run.

6. **Smoke test**: open OpenClaw, start a new session, and ask the agent to run this
   skill's smoke test (e.g. "run the LinkedIn automation skill's smoke test"). If it fails,
   report the output to the maintainer as an issue rather than troubleshooting the runtime
   yourself.

The runtime drives a dedicated Chrome profile (`CHROME_PROFILE_DIR`) that holds your live
LinkedIn session cookies — treat that profile directory as sensitive, the same as a
password store, and keep its filesystem permissions restricted to your own user.

The runtime's only expected network destinations are `linkedin.com`/`www.linkedin.com` (the
browser automation) and `api.anthropic.com` (AI-answered questions, via `ANTHROPIC_API_KEY`).
If your environment supports outbound network allowlisting, restrict the runtime to those
two hosts — traffic to anywhere else means something other than the documented automation is
running.

Once installed, ask your OpenClaw agent to start or resume a LinkedIn application sprint —
this skill tells it how to find and drive the already-installed runtime, and will ask you to
confirm before it submits any application.

## License

MIT-0 for this skill package. The separately distributed runtime has its own license terms.
