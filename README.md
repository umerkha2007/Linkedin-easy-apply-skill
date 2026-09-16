# LinkedIn Automation (OpenClaw skill)

Automates LinkedIn Easy Apply job sprints: login verification, job search, AI-answered
application questions, submission logging, and optional hiring-team connection requests.

This package contains only the OpenClaw skill definition ([SKILL.md](SKILL.md)) — no
implementation code. The automation itself runs as a separately distributed Python
runtime that you install once, outside of ClawHub.

## Setup

Two ways to get the runtime installed — pick one:

**Automatic (recommended):** set `LINKEDIN_AUTOMATION_RUNTIME_URL` to wherever the
`linkedin-automation-runtime-<version>.zip` archive is hosted (distributed separately from
this skill, e.g. a GitHub Release asset). The first time you ask your OpenClaw agent to run
a LinkedIn sprint, if no runtime is found yet, it downloads and installs it itself — see
[SKILL.md](SKILL.md) for the exact bootstrap steps it follows.

**Manual:**
1. Get the `linkedin-automation-runtime-<version>` archive.
2. Extract it, then run its installer:
   ```
   # Windows
   pwsh install.ps1

   # macOS / Linux
   ./install.sh
   ```
   This installs the runtime's Python dependencies and the Playwright Chrome browser the
   automation drives.
3. Either set `LINKEDIN_AUTOMATION_RUNTIME_DIR` to the extracted runtime's path, or move it
   to `~/.openclaw/workspace/linkedin-automation-runtime/` (the skill's default search
   path).

Either way, then configure the runtime: copy its `.env.example` to `.env` and set
`ANTHROPIC_API_KEY` at minimum. See the runtime's own `README.md` for the full settings
reference.

Once installed, ask your OpenClaw agent to start or resume a LinkedIn application sprint —
this skill tells it how to find (or bootstrap) and drive the runtime.

## License

MIT-0 for this skill package. The separately distributed runtime has its own license terms.
