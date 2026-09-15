# LinkedIn Automation (OpenClaw skill)

Automates LinkedIn Easy Apply job sprints: login verification, job search, form fill
(AI-answered open-ended questions via Claude), submission logging, and optional
hiring-team connection requests.

This repo ships a compiled automation core (`dist/lib/*.pyc`) behind a small CLI — see
[SKILL.md](SKILL.md) for the full setup and usage instructions consumed by OpenClaw.

## Quick start

```
pip install -r requirements.txt
python -m playwright install chrome
cp .env.example .env   # set ANTHROPIC_API_KEY at minimum
python dist\lib\cli.pyc login-check
python dist\lib\cli.pyc login      # if needed
python dist\lib\cli.pyc smoke      # sanity check, no submissions
python dist\lib\cli.pyc run        # run a sprint
```

## License

MIT-0 — see [SKILL.md](SKILL.md) for the full interface contract.
