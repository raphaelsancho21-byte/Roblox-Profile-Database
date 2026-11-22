"""Best-effort form filling with Playwright; never submit or bypass verification."""
from __future__ import annotations
from pathlib import Path
import os

SIGNUP_URL = "https://www.roblox.com/"

def open_autofill(username, password, console):
    """Returns (browser, context, page) if successful; caller closes after user interaction.

    Fields change occasionally; only editable username and password fields are targeted.
    Birth date, gender, CAPTCHA, security verification and submission remain manual.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("Playwright não instalado. Execute: py -m pip install playwright") from exc
    pw = sync_playwright().start()
    browser = None
    try:
        choices = [{"channel": "chrome"}, {"channel": "msedge"}]
        roots = [
            Path(os.environ.get("LOCALAPPDATA", "")) / "BraveSoftware/Brave-Browser/Application/brave.exe",
            Path(os.environ.get("PROGRAMFILES", "")) / "BraveSoftware/Brave-Browser/Application/brave.exe",
            Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Microsoft/Edge/Application/msedge.exe",
        ]
        choices.extend({"executable_path": str(path)} for path in roots if path.is_file())
        errors = []
        for choice in choices:
            try:
                browser = pw.chromium.launch(headless=False, **choice)
                break
            except Exception as exc:
                errors.append(str(exc).splitlines()[0])
        if browser is None:
            raise RuntimeError("Nenhum navegador Chromium compatível encontrado (Chrome, Edge ou Brave).")
        context = browser.new_context()
        page = context.new_page()
        page.goto(SIGNUP_URL, wait_until="domcontentloaded", timeout=30000)
        # Best-effort, non-invasive fill. Do not click signup, navigate CAPTCHAs,
        # set date of birth or react to security challenges.
        def fill_first(selectors, value):
            for selector in selectors:
                try:
                    loc = page.locator(selector).first
                    if loc.count() and loc.is_visible(timeout=1500):
                        loc.fill(value, timeout=5000)
                        return True
                except Exception:
                    continue
            return False
        username_ok = fill_first(
            ["#signup-username", "input[name='username']", "input[autocomplete='username']"],
            username)
        password_ok = fill_first(
            ["#signup-password", "input[name='password']", "input[autocomplete='new-password']"],
            password)
        if username_ok and password_ok:
            console.print("[green]✓ Username e senha preenchidos.[/green]")
        else:
            console.print("[yellow]Alguns campos não puderam ser preenchidos; conclua-os manualmente.[/yellow]")
        console.print("[dim]Data de nascimento real, CAPTCHA e envio do cadastro continuam manuais.[/dim]")
        return pw, browser, context, page
    except Exception:
        if browser:
            browser.close()
        pw.stop()
        raise

def close_session(session):
    if not session:
        return
    pw, browser, context, page = session
    try:
        browser.close()
    finally:
        pw.stop()
