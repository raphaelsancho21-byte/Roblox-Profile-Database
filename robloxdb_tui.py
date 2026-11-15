"""Interactive RobloxDB terminal interface, inspired by modern coding CLIs."""
import os
from pathlib import Path
import shlex
import webbrowser

from rich import box
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt

from robloxdb_cli import find_user, snapshot, PROFILE_DIR, CARD_DIR
from robloxdb_visual import render as visual_card
import json

console = Console()
VERSION = "0.3.0"
ACCENT = "#7c97ff"

def banner():
    title = Text()
    title.append("  ▪ ROBLOX", style="bold bright_white")
    title.append("DB", style="bold #7c97ff")
    title.append("   /   PROFILE INTELLIGENCE\n", style="bold #8393af")
    title.append("  Consultas públicas do Roblox, direto no terminal.", style="#aab5d1")
    console.print(Panel(title, border_style=ACCENT, box=box.ROUNDED, padding=(1, 1)))
    console.print("[dim]Digite um username ou UserId. Use [bold]/help[/bold] para ver comandos.[/dim]\n")

def help_screen():
    table = Table(box=box.SIMPLE, show_header=False, pad_edge=False)
    table.add_column("Comando", style="bold #9eb4ff", no_wrap=True)
    table.add_column("Descrição", style="white")
    for a,b in [
        ("4lurcx", "Consultar por username"),
        ("1", "Consultar por UserId"),
        ("/search NOME", "Consultar outra conta"),
        ("/open", "Abrir a última ficha no navegador"),
        ("/profile", "Abrir perfil original no Roblox"),
        ("/json", "Mostrar caminho do último JSON"),
        ("/clear", "Limpar a tela"),
        ("/help", "Ajuda"),
        ("/exit", "Sair"),
    ]: table.add_row(a,b)
    console.print(Panel(table, title="[bold]Comandos[/bold]", border_style="#38435c", box=box.ROUNDED))

def fmt(value):
    return "[dim]Não disponível[/dim]" if value is None else str(value)

def profile_panel(data):
    p = data.get("profile", {})
    c = data.get("social_counts", {})
    name = p.get("displayName") or p.get("name") or "Perfil"
    username = p.get("name", "desconhecido")
    user_id = p.get("id")
    header = Text()
    header.append(str(name) + "\n", style="bold bright_white")
    header.append("@" + str(username) + "  ·  ID " + str(user_id), style="#a3afd0")
    console.print(Panel(header, title="[bold #9eb4ff]RESULTADO DA PESQUISA[/bold #9eb4ff]", border_style=ACCENT, box=box.ROUNDED))
    table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2), expand=True)
    table.add_column(style="dim")
    table.add_column(style="bold bright_white")
    for label, value in [
        ("Amigos", c.get("friends")),
        ("Seguidores", c.get("followers")),
        ("Seguindo", c.get("following")),
        ("Criado em", p.get("created")),
        ("Jogos favoritos (amostra)", len(data["favorite_games"]) if isinstance(data.get("favorite_games"), list) else None),
        ("Jogos criados (amostra)", len(data["created_games"]) if isinstance(data.get("created_games"), list) else None),
        ("Itens equipados", len(data["currently_wearing_asset_ids"]) if isinstance(data.get("currently_wearing_asset_ids"), list) else None),
    ]: table.add_row(label, fmt(value))
    console.print(Panel(table, border_style="#38435c", box=box.ROUNDED))
    desc = p.get("description")
    if desc: console.print(Panel(Text(str(desc)), title="Descrição", border_style="#38435c", box=box.ROUNDED))
    for label, key in [("Jogos favoritos", "favorite_games"), ("Jogos criados", "created_games")]:
        values = data.get(key)
        if isinstance(values, list) and values:
            names = [str(x.get("name") or "Jogo") for x in values[:6]]
            console.print("[bold #9eb4ff]" + label + ":[/bold #9eb4ff] " + "  ·  ".join(names))
    console.print("[dim]Use /open para a ficha HTML com imagens ou /profile para o Roblox.[/dim]\n")

def lookup(query):
    with console.status("[#9eb4ff]Consultando informações públicas...", spinner="dots"):
        user_id = find_user(query)
        data = snapshot(user_id)
        PROFILE_DIR.mkdir(parents=True, exist_ok=True)
        CARD_DIR.mkdir(parents=True, exist_ok=True)
        json_path = PROFILE_DIR / f"{user_id}.json"
        html_path = CARD_DIR / f"{user_id}.html"
        json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        html_path.write_text(visual_card(data), encoding="utf-8")
    return data, json_path, html_path

def run(initial_query=None):
    console.clear()
    banner()
    last_data = None
    last_json = None
    last_html = None

    def search(query):
        nonlocal last_data, last_json, last_html
        try:
            if not query.strip():
                console.print("[yellow]Informe nome ou ID.[/yellow]")
                return
            last_data, last_json, last_html = lookup(query)
            console.print("[green]✓ Consulta concluída. Snapshot salvo localmente.[/green]")
            profile_panel(last_data)
        except (ValueError, OSError, KeyError) as exc:
            console.print(f"[red]Erro:[/red] {str(exc).replace('[', '(').replace(']', ')')}")
        except Exception as exc:
            console.print(f"[red]Falha na consulta:[/red] {type(exc).__name__}: {str(exc).replace('[', '(').replace(']', ')')}")

    if initial_query:
        search(initial_query)
    while True:
        try:
            command = Prompt.ask("[bold #9eb4ff]robloxdb[/bold #9eb4ff] [dim]›[/dim]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Saindo do RobloxDB.[/dim]")
            return 0
        if not command: continue
        key, _, rest = command.partition(" ")
        key = key.lower()
        if key in ("/exit", "/quit", "exit", "quit", "/q"):
            console.print("[dim]Até mais![/dim]")
            return 0
        elif key in ("/help", "help", "?"):
            help_screen()
        elif key == "/clear":
            console.clear()
            banner()
        elif key in ("/search", "/user", "/id"):
            search(rest)
        elif key == "/open":
            if last_html and last_html.exists():
                webbrowser.open(last_html.resolve().as_uri())
                console.print("[green]Ficha HTML aberta no navegador.[/green]")
            else: console.print("[yellow]Consulte um perfil primeiro.[/yellow]")
        elif key == "/profile":
            if last_data:
                uid = int(last_data["profile"]["id"])
                webbrowser.open("https://www.roblox.com/users/" + str(uid) + "/profile")
            else: console.print("[yellow]Consulte um perfil primeiro.[/yellow]")
        elif key == "/json":
            if last_json:
                console.print("[#9eb4ff]" + str(last_json) + "[/#9eb4ff]")
            else: console.print("[yellow]Consulte um perfil primeiro.[/yellow]")
        elif command.startswith("/"):
            console.print("[yellow]Comando desconhecido. Digite /help.[/yellow]")
        else:
            search(command)

if __name__ == "__main__":
    raise SystemExit(run())
