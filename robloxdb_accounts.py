"""RobloxDB registration helper: optional autofill and manual verification.

No automated submission. No password export, webhook credentials, or CAPTCHA bypass.
"""
from __future__ import annotations
import os
import re
import secrets
import string
import urllib.parse
import urllib.request
import json
import datetime as dt
import webbrowser

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm

from robloxdb_v2 import HOME, save_json, stamp
from robloxdb_autofill import open_autofill, close_session

console = Console()
STATE = HOME / "account_manager.json"
SIGNUP_URL = "https://www.roblox.com/"

def username_suggestion():
    parts = ("Nova", "Pixel", "Cobalt", "Orbit", "Comet", "Vortex", "Lunar", "Nimbus")
    suffix = ("Rider", "Studio", "Quest", "Player", "Fox", "Craft")
    return secrets.choice(parts) + secrets.choice(suffix) + str(secrets.randbelow(9000) + 1000)

def new_password():
    chars = string.ascii_letters + string.digits + "!@#$%*_-"
    return "".join(secrets.choice(chars) for _ in range(24))

def valid_username(name):
    return bool(re.fullmatch(r"[A-Za-z0-9_]{3,20}", name)) and not name.startswith("_") and not name.endswith("_")

def sanitized(entry):
    return {"username": entry["username"], "status": entry["status"], "updated_at": stamp()}

def notify_discord(username):
    """Opt-in notice only; intentionally never accepts or transmits passwords."""
    url = os.getenv("ROBLOXDB_DISCORD_WEBHOOK", "").strip()
    if not url:
        return
    parsed = urllib.parse.urlparse(url)
    if (parsed.scheme != "https" or parsed.hostname not in ("discord.com", "discordapp.com")
            or not parsed.path.startswith("/api/webhooks/")):
        console.print("[yellow]Webhook inválido. Nenhuma notificação enviada.[/yellow]")
        return
    payload = {
        "content": "RobloxDB: cadastro confirmado manualmente. Username: "
                   + username.replace("@", "") + ". Nenhuma senha foi transmitida.",
        "allowed_mentions": {"parse": []},
    }
    req = urllib.request.Request(url, method="POST",
                                 data=json.dumps(payload).encode("utf-8"),
                                 headers={"Content-Type": "application/json",
                                          "User-Agent": "RobloxDB/2.2"})
    try:
        with urllib.request.urlopen(req, timeout=10):
            pass
        console.print("[green]Notificação sem credenciais enviada ao Discord.[/green]")
    except Exception:
        console.print("[yellow]Não foi possível enviar a notificação ao Discord.[/yellow]")

def manual_account_setup():
    console.print(Panel(
        "[bold #a0b4ff]ACCOUNT MANAGER · ASSISTENTE DE CADASTRO[/bold #a0b4ff]\n"
        "Preenchimento opcional de username e senha no navegador, quando permitido.\n"
        "Data de nascimento verdadeira, CAPTCHA e envio final são manuais.\n"
        "[dim]Nenhuma senha é salva nem enviada ao Discord.[/dim]",
        border_style="#809aff"))
    count = IntPrompt.ask("Quantas contas?", default=1)
    if not 1 <= count <= 5:
        console.print("[red]Escolha de 1 a 5 contas.[/red]")
        return
    mode = Prompt.ask("Usernames", choices=["aleatorio", "manual"], default="aleatorio")
    accounts = []
    for i in range(count):
        name = Prompt.ask(f"Username {i+1}").strip() if mode == "manual" else username_suggestion()
        if not valid_username(name):
            console.print("[red]Username inválido; use 3–20 caracteres válidos. O Roblox validará disponibilidade.[/red]")
            return
        accounts.append({"username": name, "status": "pendente"})
    save_json(STATE, {"accounts": [sanitized(a) for a in accounts]})
    for i, account in enumerate(accounts, 1):
        name = account["username"]
        while True:
            raw_dob = Prompt.ask(f"Data de nascimento VERDADEIRA para @{name} (DD/MM/AAAA)")
            try:
                birth_date = dt.datetime.strptime(raw_dob, "%d/%m/%Y").date()
                if birth_date > dt.date.today() or birth_date.year < 1900:
                    raise ValueError("Data fora do intervalo aceito")
                break
            except ValueError:
                console.print("[yellow]Data inválida. Use DD/MM/AAAA, sem inventar a idade.[/yellow]")
        password = new_password()
        console.print(Panel(
            f"[bold]{i}/{count}[/bold]  @{name}\n"
            "Senha sugerida abaixo, exibida apenas uma vez. Guarde-a em um gerenciador de senhas.",
            border_style="#4d5d86"))
        console.print("[yellow]Senha:[/yellow] " + password)
        session = None
        try:
            while True:
                option = Prompt.ask("Ação", choices=["preencher", "manual", "tentar", "concluido", "pular"],
                                    default="preencher")
                if option in ("preencher", "tentar"):
                    if session:
                        close_session(session)
                        session = None
                    try:
                        session = open_autofill(name, password, birth_date, console)
                    except Exception as exc:
                        console.print("[yellow]Preenchimento não disponível: " + type(exc).__name__ +
                                      ". Use 'manual', 'tentar' ou 'pular'.[/yellow]")
                    continue
                if option == "manual":
                    if not session:
                        webbrowser.open(SIGNUP_URL)
                    console.print("[cyan]Complete o cadastro no navegador; retorne para confirmar ou pular.[/cyan]")
                    continue
                if option == "concluido":
                    if not Confirm.ask("Você criou a conta e consegue entrar nela?", default=False):
                        continue
                    account["status"] = "confirmada pelo usuário"
                    save_json(STATE, {"accounts": [sanitized(a) for a in accounts]})
                    notify_discord(name)
                    break
                if option == "pular":
                    account["status"] = "pendente"
                    save_json(STATE, {"accounts": [sanitized(a) for a in accounts]})
                    break
        finally:
            if session:
                close_session(session)
    total = sum(a["status"] == "confirmada pelo usuário" for a in accounts)
    console.print(Panel(
        f"[bold #a0b4ff]RESUMO[/bold #a0b4ff]\n{total}/{count} cadastros confirmados por você.\n"
        f"Registro sem senhas: {STATE}",
        border_style="#809aff"))

if __name__ == "__main__":
    manual_account_setup()
