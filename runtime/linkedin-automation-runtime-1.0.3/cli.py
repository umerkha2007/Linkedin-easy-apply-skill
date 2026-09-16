"""Entrypoint for the separately distributed linkedin-automation Python runtime.

This file ships as plain, readable .py text — it's thin CLI orchestration only, no
proprietary selectors/business logic. The real automation modules (easy_apply, bot_logic,
ai_answer, daily_limit, connect_hiring_team, human_utils) ship next to this file as
compiled bytecode (*.pyc, Python-version-pinned — see build/compile.py) and import
normally once this directory is on sys.path. This runtime is distributed independently of
the public ClawHub skill package (dist/skill/), which contains no code at all — see
dist/skill/SKILL.md for how the skill locates and invokes this runtime.

Subcommands:
  login-check   Fast, no-browser check of whether the profile has a valid li_at cookie.
  login         Open the profile in a real browser and wait for the user to log in.
  verify        Fresh browser launch, confirm the profile lands on the LinkedIn feed.
  smoke         Live smoke test: login works + at least one Easy Apply candidate found.
  run           Run the actual Easy Apply sprint (same args as easy_apply.py).
"""
import asyncio
import os
import shutil
import sqlite3
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def _profile_dir():
    return os.environ.get("CHROME_PROFILE_DIR") or os.path.join(
        os.path.expanduser("~"), ".openclaw", "workspace", ".playwright-profile"
    )


def cmd_login_check():
    profile_dir = _profile_dir()
    src = os.path.join(profile_dir, "Default", "Network", "Cookies")
    if not os.path.exists(src):
        print("needs_login")
        return
    tmp = tempfile.mktemp(suffix=".db")
    try:
        shutil.copy(src, tmp)
        conn = sqlite3.connect(tmp)
        rows = conn.execute("SELECT 1 FROM cookies WHERE name='li_at'").fetchall()
        conn.close()
        print("logged_in" if rows else "needs_login")
    except Exception:
        print("needs_login")
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass


async def _cmd_login_async():
    from playwright.async_api import async_playwright

    profile_dir = _profile_dir()
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            profile_dir, headless=False, channel="chrome", args=["--no-sandbox"]
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto("https://www.linkedin.com/login", timeout=30000, wait_until="domcontentloaded")
        print("Waiting for login (including 2FA if prompted) ...")
        await page.wait_for_url("**/feed/**", timeout=300000)
        print("Login detected.")
        await ctx.close()


async def _cmd_verify_async():
    from playwright.async_api import async_playwright

    profile_dir = _profile_dir()
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            profile_dir, headless=False, channel="chrome", args=["--no-sandbox"]
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto("https://www.linkedin.com/feed", timeout=20000, wait_until="domcontentloaded")
        title = await page.title()
        ok = "/feed" in page.url and title.startswith("Feed")
        print("verified" if ok else f"not_verified url={page.url} title={title}")
        await ctx.close()


async def _cmd_smoke_async():
    from playwright.async_api import async_playwright
    import easy_apply as ea

    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            ea.PROFILE, headless=False, channel="chrome", args=["--no-sandbox"]
        )
        page = browser.pages[0] if browser.pages else await browser.new_page()

        await page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded", timeout=20000)
        login = {"loggedIn": False, "url": page.url}
        for _ in range(4):
            await page.wait_for_timeout(2000)
            login = await page.evaluate("""() => {
                const onLoginPage = location.href.includes('/login') || location.href.includes('/checkpoint/');
                const onFeed = location.href.includes('/feed');
                return { loggedIn: !onLoginPage && onFeed, url: location.href };
            }""")
            if login["loggedIn"]:
                break
        print(f"[1/2] Login check: {login}")
        assert login["loggedIn"], "NOT LOGGED IN — run 'login' first"

        candidates = await ea.get_job_candidates(page, ea.SEARCH_QUERIES[0], scan_per_page=25)
        print(f"[2/2] Found {len(candidates)} Easy Apply candidate(s) on first search page")
        assert len(candidates) >= 1, "Scraper found zero candidates — selectors may be stale"

        print("\nSMOKE TEST PASSED — login works and candidates are discoverable. No applications were submitted.")
        await browser.close()


def cmd_run(argv):
    import easy_apply as ea

    sys.argv = ["easy_apply"] + argv
    asyncio.run(ea.main())


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd, rest = sys.argv[1], sys.argv[2:]
    if cmd == "login-check":
        cmd_login_check()
    elif cmd == "login":
        asyncio.run(_cmd_login_async())
    elif cmd == "verify":
        asyncio.run(_cmd_verify_async())
    elif cmd == "smoke":
        asyncio.run(_cmd_smoke_async())
    elif cmd == "run":
        cmd_run(rest)
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
