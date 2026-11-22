"""Manual Roblox registration assistant. No automated signups or credential collection."""
from __future__ import annotations
import json
import re
import secrets
import string
import webbrowser
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.progress import Progress, BarColumn, TextColumn

from robloxdb_v2 import HOME, save_json, read_json, stamp

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

def manual_account_setup():
    console.print(Panel("[bold #a0b4ff]ACCOUNT MANAGER[/bold #a0b4ff]\n"
                        "Assistente de cadastro manual. Nenhuma conta é criada automaticamente.\n"
                        "[dim]Senhas não são salvas pelo RobloxDB ou enviadas ao Discord.[/dim]",
                        border_style="#809aff"))
    count = IntPrompt.ask("Quantas contas?", default=1)
    if count < 1 or count > 5:
        console.print("[red]Escolha entre 1 e 5 contas.[/red]")
        return
    mode = Prompt.ask("Usernames", choices=["aleatorio", "manual"], default="aleatorio")
    accounts = []
    for index in range(count):
        if mode == "manual":
            name = Prompt.ask(f"Username da conta {index+1}").strip()
            if not valid_username(name):
                console.print("[yellow]Formato inválido. Use 3–20 letras, números ou underscore; a disponibilidade será validada pelo Roblox.[/yellow]")
                return
        else:
            name = username_suggestion()
        accounts.append({"username": name, "status": "pendente"})
    save_json(STATE, {"accounts": [sanitized(a) for a in accounts]})
    console.print("[dim]Informe a data de nascimento verdadeira diretamente no cadastro oficial. Não escolha datas aleatórias.[/dim]")
    for i, account in enumerate(accounts):
        username = account["username"]
        console.print(Panel(f"[bold]{i+1}/{count}[/bold]  @{username}\n"
                            "Abra o cadastro oficial e complete as etapas no navegador.\n"
                            "Se o Roblox pedir CAPTCHA ou outra verificação, conclua manualmente.",
                            border_style="#4d5d86"))
        password = new_password()
        console.print("[yellow]Senha sugerida (exibida uma vez; NÃO salva pelo programa):[/yellow]")
        console.print(password)
        console.print("[dim]Copie para seu gerenciador de senhas antes de continuar. Se preferir, use uma senha criada por você.[/dim]")
        try:
            webbrowser.open(SIGNUP_URL)
        except Exception:
            console.print("[yellow]Não foi possível abrir o navegador.[/yellow]")
        while True:
            result = Prompt.ask("Resultado", choices=["concluido", "tentar", "manual", "pular"], default="manual")
            if result == "tentar":
                try:
                    opened = webbrowser.open(SIGNUP_URL)
                    console.print("[green]Navegador solicitado.[/green]" if opened else
                                  "[yellow]Não foi possível abrir automaticamente. Entre em https://www.roblox.com/.[/yellow]")
                except Exception:
                    console.print("[yellow]Abra https://www.roblox.com/ manualmente.[/yellow]")
                continue
            if result == "manual":
                console.print("[cyan]Finalize o formulário oficial do Roblox no navegador e volte aqui.[/cyan]")
                console.print("[dim]Você pode escolher 'concluido', 'tentar' ou 'pular' depois.[/dim]")
                continue
            if result == "concluido":
                if not Confirm.ask("Você concluiu o cadastro e consegue entrar nessa conta?", default=False):
                    continue
                account["status"] = "confirmada pelo usuário"
            else:
                account["status"] = "pendente"
            save_json(STATE, {"accounts": [sanitized(a) for a in accounts]})
            break
    confirmed = sum(1 for item in accounts if item["status"] == "confirmada pelo usuário")
    console.print(Panel(f"[bold #a0b4ff]Resumo[/bold #a0b4ff]\n"
                        f"{confirmed}/{len(accounts)} cadastros confirmados por você.\n"
                        f"Registro local sem senhas: {STATE}\n"
                        "O RobloxDB não pode comprovar sozinho a criação das contas.",
                        border_style="#809aff"))

if __name__ == "__main__":
    manual_account_setup()
