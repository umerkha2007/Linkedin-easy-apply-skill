# LinkedIn Automation (OpenClaw skill)

Automates LinkedIn Easy Apply job sprints: login verification, job search, AI-answered
application questions, submission logging, and optional hiring-team connection requests.

This package contains only the OpenClaw skill definition ([SKILL.md](SKILL.md)) — no
implementation code. The automation itself runs as a separately distributed Python
runtime that you install once, outside of ClawHub.

## Setup

The runtime is installed manually, once, before you ever ask the agent to run a sprint —
this skill never downloads or executes anything itself.

1. Get the `linkedin-automation-runtime-<version>` archive and its published `.sha256`
   digest from wherever the maintainer distributed them (e.g. a GitHub Release asset).
   Prefer a specific pinned version over "latest" — treat any archive without a published
   digest as untrusted and do not install it.
2. Verify the archive **before** extracting it — a `cli.py` file existing inside is not
   itself a trust signal, only a shape check:
   ```
   # Windows
   Get-FileHash linkedin-automation-runtime-<version>.zip -Algorithm SHA256

   # macOS / Linux
   sha256sum linkedin-automation-runtime-<version>.zip
   ```
   Confirm the output matches the published `.sha256` file exactly before continuing. If it
   doesn't match, stop — do not extract or run anything from that archive.
3. Extract it, then run its installer yourself:
   ```
   # Windows
   pwsh install.ps1

   # macOS / Linux
   ./install.sh
   ```
   This installs the runtime's Python dependencies and the Playwright Chrome browser the
   automation drives. Review `install.ps1`/`install.sh`/`requirements.txt` yourself before
   running them if you don't already trust the source you got the archive from.
4. Either set `LINKEDIN_AUTOMATION_RUNTIME_DIR` to the extracted runtime's path, or move it
   to `~/.openclaw/workspace/linkedin-automation-runtime/` (the skill's default search
   path). Use an absolute path you control — not a shared or world-writable directory,
   and not a symlink to one.
5. Configure the runtime: copy its `.env.example` to `.env` and set `ANTHROPIC_API_KEY` at
   minimum. See the runtime's own `README.md` for the full settings reference.

The runtime drives a dedicated Chrome profile (`CHROME_PROFILE_DIR`) that holds your live
LinkedIn session cookies — treat that profile directory as sensitive, the same as a
password store, and keep its filesystem permissions restricted to your own user.

Once installed, ask your OpenClaw agent to start or resume a LinkedIn application sprint —
this skill tells it how to find and drive the already-installed runtime.

## License

MIT-0 for this skill package. The separately distributed runtime has its own license terms.
