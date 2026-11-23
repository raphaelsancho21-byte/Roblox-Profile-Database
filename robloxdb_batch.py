"""Browser-assisted batch registration: independent contexts, no CAPTCHA bypass.

All accounts have a user-supplied truthful date of birth. This helper fills
visible signup controls and leaves final submission to the user.
Never treats a click or challenge as proof the account was created.
"""
from __future__ import annotations
import os
from pathlib import Path
from robloxdb_autofill import SIGNUP_URL, MONTHS

FORM_MARKERS = ("#signup-username, #signup-password, #MonthDropdown, "
                "input[name='username'], input[autocomplete='new-password'], "
                "select[name='birthdayMonth']")
SUBMIT_SELECTORS = (
    "#signup-button", "button[type='submit']",
    "button:has-text('Cadastrar')", "button:has-text('Sign Up')",
    "button:has-text('Criar conta')", "button:has-text('Inscrever-se')"
)

def pick_browser(playwright):
    roots = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "BraveSoftware/Brave-Browser/Application/brave.exe",
        Path(os.environ.get("PROGRAMFILES", "")) / "BraveSoftware/Brave-Browser/Application/brave.exe",
        Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Microsoft/Edge/Application/msedge.exe",
    ]
    candidates = [{"channel": "chrome"}, {"channel": "msedge"}]
    candidates.extend({"executable_path": str(p)} for p in roots if p.is_file())
    for options in candidates:
        try:
            return playwright.chromium.launch(headless=False, **options)
        except Exception:
            pass
    raise RuntimeError("Instale Chrome, Edge ou Brave para usar o preenchimento.")

def select_first(page, selectors, values):
    for css in selectors:
        try:
            field = page.locator(css).first
            if not field.count() or not field.is_visible():
                continue
            for value in values:
                for method in ("value", "label"):
                    try:
                        field.select_option(**{method: str(value)}, timeout=1200)
                        return True
                    except Exception:
                        pass
        except Exception:
            continue
    return False

def fill_first(page, selectors, value):
    for css in selectors:
        try:
            field = page.locator(css).first
            if field.count() and field.is_visible():
                field.fill(value, timeout=5000)
                return True
        except Exception:
            pass
    return False

def prepare_page(page, account):
    try:
        page.goto(SIGNUP_URL, wait_until="domcontentloaded", timeout=35000)
        page.locator(FORM_MARKERS).first.wait_for(state="visible", timeout=20000)
    except Exception:
        return {"status": "manual", "message": "Formulário não apareceu; complete manualmente."}

    birthday = account["birth_date"]
    month = birthday.month
    fields = {
        "Mês": select_first(page, ("#MonthDropdown", "select[name='birthdayMonth']", "select[name='month']"),
                            (month, str(month).zfill(2), MONTHS[month-1], MONTHS[month-1][:3])),
        "Dia": select_first(page, ("#DayDropdown", "select[name='birthdayDay']", "select[name='day']"),
                            (birthday.day, str(birthday.day).zfill(2))),
        "Ano": select_first(page, ("#YearDropdown", "select[name='birthdayYear']", "select[name='year']"),
                            (birthday.year,)),
        "Username": fill_first(page, ("#signup-username", "input[name='username']", "input[autocomplete='username']"),
                               account["username"]),
        "Senha": fill_first(page, ("#signup-password", "input[name='password']", "input[autocomplete='new-password']"),
                            account["password"]),
    }
    if not all(fields.values()):
        missing = ", ".join(label for label, ok in fields.items() if not ok)
        return {"status": "manual", "message": "Campos pendentes: " + missing, "fields": fields}
    # Never click signup automatically. Once the site displays a security
    # challenge, any automated retry/reload can discard its state.
    return {"status": "ready", "message":
            "Campos preparados. Clique Cadastrar manualmente e conclua a verificação sem recarregar a página.",
            "fields": fields}

class BatchBrowser:
    """Keep isolated sessions open while the user finishes verifications."""
    def __init__(self):
        self.pw = None
        self.browser = None
        self.contexts = []
        self.pages = []

    def start(self):
        from playwright.sync_api import sync_playwright
        self.pw = sync_playwright().start()
        try:
            self.browser = pick_browser(self.pw)
        except Exception:
            self.pw.stop()
            self.pw = None
            raise

    def prepare(self, account):
        if not self.browser:
            raise RuntimeError("Navegador não iniciado")
        # A fresh context isolates cookies/session for each account.
        context = self.browser.new_context(viewport={"width": 1180, "height": 790}, locale="pt-BR")
        self.contexts.append(context)
        page = context.new_page()
        self.pages.append(page)
        return prepare_page(page, account)

    def retry(self, index, account):
        return {"status": "manual", "message":
                "Recarregar apagaria a sessão/CAPTCHA. Corrija os campos na janela existente; "
                "se o Roblox rejeitou a verificação, inicie uma nova tentativa manualmente."}

    def close(self):
        if self.browser:
            try:
                self.browser.close()
            except Exception:
                pass
        if self.pw:
            try:
                self.pw.stop()
            except Exception:
                pass
