"""Conservative Playwright-assisted form filling (no submission or CAPTCHA automation)."""
from __future__ import annotations

import os
from pathlib import Path

SIGNUP_URL = "https://www.roblox.com/pt?p=reg"
MONTHS = ("January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December")


def open_autofill(username, password, birth_date, console):
    """Open visible signup page and fill supported fields when available.

    Date of birth must be supplied truthfully. No automatic submission, challenge
    handling, hidden state manipulation, or verification bypass.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError("Playwright não está instalado. Use: py -m pip install playwright") from exc

    pw = sync_playwright().start()
    browser = None
    try:
        roots = [
            Path(os.environ.get("LOCALAPPDATA", "")) / "BraveSoftware/Brave-Browser/Application/brave.exe",
            Path(os.environ.get("PROGRAMFILES", "")) / "BraveSoftware/Brave-Browser/Application/brave.exe",
            Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Microsoft/Edge/Application/msedge.exe",
        ]
        choices = [{"channel": "chrome"}, {"channel": "msedge"}]
        choices += [{"executable_path": str(p)} for p in roots if p.is_file()]
        for choice in choices:
            try:
                browser = pw.chromium.launch(headless=False, **choice)
                break
            except Exception:
                continue
        if browser is None:
            raise RuntimeError("Não consegui iniciar Chrome, Edge ou Brave via Playwright.")
        context = browser.new_context(viewport={"width": 1280, "height": 850}, locale="pt-BR")
        page = context.new_page()
        page.goto(SIGNUP_URL, wait_until="domcontentloaded", timeout=35000)

        # Avoid racing with JavaScript-rendered signup form.
        markers = ("#signup-username, #signup-password, #MonthDropdown, "
                   "input[name='username'], input[autocomplete='new-password'], "
                   "select[name='birthdayMonth']")
        try:
            page.locator(markers).first.wait_for(state="visible", timeout=20000)
        except Exception:
            console.print("[yellow]O formulário não apareceu. Talvez o Roblox tenha exibido login, "
                          "um bloqueio, ou mudado o layout. Conclua manualmente nesta aba.[/yellow]")
            return pw, browser, context, page

        def select_first(selectors, options):
            for css in selectors:
                try:
                    field = page.locator(css).first
                    if field.count() == 0 or not field.is_visible():
                        continue
                    for option in options:
                        for key in ("value", "label"):
                            try:
                                field.select_option(**{key: str(option)}, timeout=1200)
                                return True
                            except Exception:
                                pass
                except Exception:
                    pass
            return False

        def fill_first(selectors, value):
            for css in selectors:
                try:
                    field = page.locator(css).first
                    if field.count() and field.is_visible():
                        field.fill(value, timeout=5000)
                        return True
                except Exception:
                    pass
            return False

        month = birth_date.month
        month_ok = select_first(
            ("#MonthDropdown", "select[name='birthdayMonth']", "select[name='month']"),
            (month, str(month).zfill(2), MONTHS[month-1], MONTHS[month-1][:3]))
        day_ok = select_first(
            ("#DayDropdown", "select[name='birthdayDay']", "select[name='day']"),
            (birth_date.day, str(birth_date.day).zfill(2)))
        year_ok = select_first(
            ("#YearDropdown", "select[name='birthdayYear']", "select[name='year']"),
            (birth_date.year,))
        username_ok = fill_first(
            ("#signup-username", "input[name='username']", "input[autocomplete='username']"),
            username)
        password_ok = fill_first(
            ("#signup-password", "input[name='password']", "input[autocomplete='new-password']"),
            password)

        for label, ok in (
            ("Mês", month_ok), ("Dia", day_ok), ("Ano", year_ok),
            ("Username", username_ok), ("Senha", password_ok)
        ):
            console.print(("[green]✓[/green]" if ok else "[yellow]![/yellow]")
                          + " " + label + (": preenchido" if ok else ": preencher manualmente"))

        console.print("[dim]Revise todos os campos na janela aberta. "
                      "Você deve resolver as verificações e enviar o cadastro manualmente.[/dim]")
        return pw, browser, context, page
    except Exception:
        if browser is not None:
            browser.close()
        pw.stop()
        raise


def close_session(session):
    if session:
        pw, browser, context, page = session
        try:
            browser.close()
        finally:
            pw.stop()
