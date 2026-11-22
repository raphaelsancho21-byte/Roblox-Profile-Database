"""Best-effort form filling with Playwright; never submit or bypass verification."""
from __future__ import annotations
from pathlib import Path
import os
import datetime as dt

SIGNUP_URL = "https://www.roblox.com/"

def open_autofill(username, password, birth_date, console):
    """Returns (browser, context, page) if successful; caller closes after user interaction.

    Birth date is supplied by the user and filled BEFORE username and password.
    CAPTCHA, security verification and submission remain manual.
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
        # The Roblox sign-up form usually displays birthday selectors first.
        # No random DOB, no automatic submit, no CAPTCHA interaction.
        def select_first(selectors, values):
            for selector in selectors:
                try:
                    loc = page.locator(selector).first
                    if not loc.count() or not loc.is_visible():
                        continue
                    for value in values:
                        try:
                            loc.select_option(value=str(value), timeout=2500)
                            return True
                        except Exception:
                            try:
                                loc.select_option(label=str(value), timeout=2500)
                                return True
                            except Exception:
                                pass
                except Exception:
                    continue
            return False

        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        month_num = birth_date.month
        month_label = months[month_num - 1]
        month_ok = select_first(
            ["#MonthDropdown", "select[name='birthdayMonth']", "select[name='month']"],
            [month_num, str(month_num).zfill(2), month_label, month_label[:3]])
        day_ok = select_first(
            ["#DayDropdown", "select[name='birthdayDay']", "select[name='day']"],
            [birth_date.day, str(birth_date.day).zfill(2)])
        year_ok = select_first(
            ["#YearDropdown", "select[name='birthdayYear']", "select[name='year']"],
            [birth_date.year])
        dob_ok = month_ok and day_ok and year_ok
        if dob_ok:
            console.print("[green]✓ Data de nascimento preenchida primeiro.[/green]")
        else:
            console.print("[yellow]Não consegui preencher todos os campos de nascimento. "
                          "Corrija-os manualmente antes de continuar.[/yellow]")

        def fill_first(selectors, value):
            for selector in selectors:
                try:
                    loc = page.locator(selector).first
                    if loc.count() and loc.is_visible():
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
            console.print("[green]✓ Username e senha preenchidos após a data.[/green]")
        else:
            console.print("[yellow]Alguns campos de username/senha não puderam ser preenchidos; "
                          "conclua manualmente.[/yellow]")
        console.print("[dim]CAPTCHA, outras verificações e envio final continuam manuais.[/dim]")
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
