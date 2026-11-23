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
from robloxdb_batch import BatchBrowser

console = Console()
STATE = HOME / "account_manager.json"
SIGNUP_URL = "https://www.roblox.com/pt?p=reg"

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
        "[bold #a0b4ff]ACCOUNT MANAGER · LOTE DE CADASTROS[/bold #a0b4ff]\n"
        "Prepara de 1 a 5 contas em janelas com sessões independentes.\n"
        "Preenche nascimento, username e senha. Você clica Cadastrar.\n"
        "CAPTCHA/verificações e confirmação final são sua responsabilidade.\n"
        "[dim]As senhas nunca são gravadas ou enviadas ao Discord.[/dim]",
        border_style="#809aff"))
    count = IntPrompt.ask("Quantas contas (1–5)?", default=1)
    if not 1 <= count <= 5:
        console.print("[red]Escolha de 1 a 5 contas.[/red]")
        return
    mode = Prompt.ask("Usernames", choices=["aleatorio", "manual"], default="aleatorio")
    accounts = []
    for i in range(count):
        username = Prompt.ask(f"Username {i+1}").strip() if mode == "manual" else username_suggestion()
        if not valid_username(username):
            console.print("[red]Username inválido. O Roblox também verificará disponibilidade.[/red]")
            return
        while True:
            raw = Prompt.ask(f"Data de nascimento VERDADEIRA de @{username} (DD/MM/AAAA)")
            try:
                dob = dt.datetime.strptime(raw, "%d/%m/%Y").date()
                if dob > dt.date.today() or dob.year < 1900:
                    raise ValueError()
                break
            except ValueError:
                console.print("[yellow]Data inválida. Use uma data verdadeira em DD/MM/AAAA.[/yellow]")
        account = {"username": username, "birth_date": dob,
                   "password": new_password(), "status": "pendente"}
        accounts.append(account)
    save_json(STATE, {"accounts": [sanitized(a) for a in accounts]})

    console.print("[bold #a0b4ff]Guarde as senhas antes de prosseguir.[/bold #a0b4ff]")
    for i, account in enumerate(accounts, 1):
        console.print(f"[yellow]{i}. @{account['username']}:[/yellow] {account['password']}")
    if not Confirm.ask("Senhas guardadas em um gerenciador seguro. Abrir as janelas?", default=False):
        console.print("[dim]Nenhum cadastro iniciado.[/dim]")
        return

    batch = BatchBrowser()
    try:
        batch.start()
        console.print("[cyan]Abrindo janelas independentes e preenchendo os formulários...[/cyan]")
        for i, account in enumerate(accounts):
            console.print(f"[#a0b4ff]{i+1}/{count}[/#a0b4ff] Preparando @{account['username']}...")
            try:
                result = batch.prepare(account)
            except Exception as exc:
                result = {"status": "manual", "message": "Falha na abertura do formulário: " + type(exc).__name__}
            account["progress"] = result
            color = "green" if result["status"] == "ready" else "yellow"
            console.print(f"[{color}]{result['message']}[/{color}]")
        console.print(Panel(
            "Formulários preparados. Clique Cadastrar e resolva o CAPTCHA em cada janela.\n"
            "[dim]Não recarregue a janela durante uma verificação. Só marque concluído após entrar na conta.[/dim]",
            border_style="#809aff"))

        for i, account in enumerate(accounts):
            username = account["username"]
            console.print(f"\n[bold]Resultado da conta {i+1}/{count}: @{username}[/bold]")
            while True:
                answer = Prompt.ask("Ação", choices=["concluido","tentar","manual","pular"], default="manual")
                if answer == "tentar":
                    try:
                        result = batch.retry(i, account)
                        console.print("[cyan]" + result["message"] + "[/cyan]")
                    except Exception as exc:
                        console.print("[yellow]Falha ao repetir preenchimento: " +
                                      type(exc).__name__ + "[/yellow]")
                    continue
                if answer == "manual":
                    console.print("[cyan]Use a janela correspondente e depois retorne para marcar concluído ou pular.[/cyan]")
                    continue
                if answer == "concluido":
                    if not Confirm.ask("Você conseguiu criar e acessar esta conta?", default=False):
                        continue
                    account["status"] = "confirmada pelo usuário"
                    notify_discord(username)
                else:
                    account["status"] = "pendente"
                save_json(STATE, {"accounts": [sanitized(a) for a in accounts]})
                break
    except Exception as exc:
        console.print("[red]Falha no navegador: " + str(exc).replace("[","(").replace("]",")") + "[/red]")
    finally:
        batch.close()
        save_json(STATE, {"accounts": [sanitized(a) for a in accounts]})
        confirmed = sum(a["status"] == "confirmada pelo usuário" for a in accounts)
        console.print(Panel(
            f"[bold]Resumo:[/bold] {confirmed}/{count} contas confirmadas pelo usuário.\n"
            f"Dados locais (sem senhas): {STATE}",
            border_style="#809aff"))

if __name__ == "__main__":
    manual_account_setup()
