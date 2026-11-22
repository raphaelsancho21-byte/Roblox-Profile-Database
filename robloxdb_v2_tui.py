"""RobloxDB V2 immersive terminal workspace."""
from __future__ import annotations
import os
import sys
import time
import webbrowser
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt
from rich.live import Live
from rich.align import Align
from rich import box

import robloxdb_v2 as db

console = Console(highlight=False)
ACCENT = "#8fa5ff"
LAST = {"user": None, "game": None, "servers": []}

def startup():
    console.clear()
    frames = [
        "◌",
        "◔",
        "◑",
        "◕",
        "●",
    ]
    can_animate = db.settings().get("animations", True) and console.is_terminal and not os.getenv("CI")
    if can_animate:
        with Live(Panel(Align.center("[bold #a9baff]◆ ROBLOXDB[/bold #a9baff]\n[dim]Inicializando módulos...[/dim]"),
                        border_style="#516497", padding=(1, 3)), console=console, refresh_per_second=16, transient=True) as live:
            for i in range(14):
                live.update(Panel(Align.center(f"[bold #a9baff]◆ ROBLOXDB[/bold #a9baff]\n[dim]{frames[i % len(frames)]} Carregando workspace · {min(100,(i+1)*8)}%[/dim]"),
                                  border_style=ACCENT, padding=(1, 3)))
                time.sleep(.045)
    title = Text(justify="center")
    title.append("◆ ", style=ACCENT)
    title.append("ROBLOX", style="bold white")
    title.append("DB", style="bold #a2b5ff")
    title.append("   V2", style="bold #91a1c2")
    footer = Text("PROFILE EXPLORER  /  PUBLIC DATA WORKSPACE", style="#8799bb", justify="center")
    console.print(Panel(Align.center(Text.assemble(title, "\n", footer)), border_style=ACCENT,
                        box=box.ROUNDED, padding=(1,2)))
    console.print("[#8897b3]  Pesquise perfis, explore servidores e organize suas próprias ocorrências.[/#8897b3]")
    console.print("[dim]  Digite /help para comandos. Dados privados não são acessíveis.[/dim]\n")

def table(title, columns, rows, limit=25):
    t = Table(title=title, box=box.ROUNDED, border_style="#3b4863", header_style="bold #9db2ff", show_lines=False, expand=True)
    for col in columns:
        t.add_column(col, overflow="fold")
    for row in rows[:limit]:
        t.add_row(*[str(x if x is not None else "—") for x in row])
    console.print(t)

def profile(data):
    p = data["profile"]; c = data.get("social_counts", {})
    console.print(Panel(f"[bold]{p.get('displayName') or p.get('name')}[/bold]\n[#9fafd0]@{p.get('name')}  •  UserId {p.get('id')}[/#9fafd0]\n"
                        f"[dim]{p.get('description') or 'Sem descrição pública'}[/dim]",
                        title="[bold #99adff]PERFIL[/bold #99adff]", border_style=ACCENT))
    table("Estatísticas", ["Amigos","Seguidores","Seguindo","Jogos favoritos","Jogos criados"],
          [[c.get("friends"),c.get("followers"),c.get("following"),
            len(data["favorite_games"]) if isinstance(data.get("favorite_games"),list) else None,
            len(data["created_games"]) if isinstance(data.get("created_games"),list) else None]])
    status = data.get("presence") or {}
    label = status.get("status", "Indisponível")
    shade = {"Online": "green", "Jogando": "bright_green", "No Studio": "cyan", "Offline": "dim", "Offline segundo API": "yellow"}.get(label, "yellow")
    console.print(f"[{shade}]● {label}[/{shade}] [dim](consulta pontual; não garante atividade real)[/dim]")
    if status.get("reason"):
        console.print("[dim]  " + str(status["reason"]) + "[/dim]")
    console.print("[dim]/presence atualiza o status · /open abre a ficha · /join solicita entrada autorizada[/dim]")

def help_screen():
    rows = [
        ("/user NOME", "Pesquisar perfil por username exato ou UserId"),
        ("/game PLACE_ID", "Detalhes de jogo por PlaceId, URL ou u:UniverseId"),
        ("/servers [PÁGINAS]", "Servidores públicos do último jogo, até 5 páginas"),
        ("/available", "Mostrar servidores com vagas da última consulta"),
        ("/open", "Abrir ficha visual do último perfil no navegador"),
        ("/presence", "Atualizar status de presença do último usuário"),
        ("/join", "Solicitar entrada no jogo pelo Roblox, se autorizado"),
        ("/save user|game|server", "Favoritar último perfil, jogo ou primeiro servidor"),
        ("/favorites", "Ver favoritos locais"),
        ("/unsave TIPO ID", "Remover favorito"),
        ("/case", "Criar ocorrência local (formulário no terminal)"),
        ("/cases", "Consultar ocorrências"),
        ("/close ID", "Fechar ocorrência"),
        ("/history", "Histórico local de pesquisas"),
        ("/compare A B", "Comparar dois perfis públicos"),
        ("/export json|csv|html|pdf", "Exportar perfil atual"),
        ("/diagnose", "Diagnosticar APIs Roblox"),
        ("/animations on|off", "Habilitar/desabilitar animações"),
        ("/clear", "Limpar o terminal"),
        ("/help  /exit", "Ajuda / sair"),
    ]
    table("CENTRAL DE COMANDOS", ["Comando", "Função"], rows, 40)

def get_user(key):
    with console.status("[#8fa5ff]Buscando informações públicas...", spinner="dots"):
        value = db.lookup_user(key)
    LAST["user"] = value
    profile(value)

def get_game(key):
    with console.status("[#8fa5ff]Consultando experiência...", spinner="dots"):
        value = db.game_from_input(key)
    LAST["game"] = value
    table("EXPERIÊNCIA", ["Campo","Valor"],
          [("Nome",value.get("name")),("UniverseId",value.get("id")),
           ("PlaceId",(value.get("rootPlace") or {}).get("id")),
           ("Jogadores",value.get("playing")),("Visitas",value.get("visits")),
           ("Criador",(value.get("creator") or {}).get("name"))])
    console.print("[dim]Digite /servers para listar servidores públicos.[/dim]")

def get_servers(arg="", available=False):
    if not LAST["game"]:
        console.print("[yellow]Use /game PLACE_ID primeiro.[/yellow]"); return
    pages = int(arg) if arg.strip().isdigit() else db.settings().get("server_pages",1)
    with console.status("[#8fa5ff]Consultando servidores públicos...", spinner="dots"):
        entries, more = db.game_servers(LAST["game"],pages=pages,available_only=available)
    LAST["servers"] = entries
    if available:
        entries = [s for s in entries if int(s.get("playing",0)) < int(s.get("maxPlayers",0))]
    table("SERVIDORES PÚBLICOS", ["Nº","Jogadores","Ping","FPS","ID (prefixo)"],
          [(str(i+1), str(s.get("playing","?"))+"/"+str(s.get("maxPlayers","?")),
            str(s.get("ping","?"))+"ms",s.get("fps"),
            str(s.get("id",""))[:12]+"…") for i,s in enumerate(entries)], 30)
    console.print(f"[dim]{len(entries)} servidores consultados (até 5 páginas)."
                  + (" Existem mais páginas." if more else "") +
                  " A API não fornece os nomes dos jogadores presentes.[/dim]")

def open_card():
    data = LAST["user"]
    if not data:
        console.print("[yellow]Pesquise um perfil primeiro.[/yellow]"); return
    from robloxdb_visual import render
    path = db.HOME / "cards" / (str(data["profile"]["id"]) + ".html")
    path.parent.mkdir(parents=True, exist_ok=True)
    with console.status("[#8fa5ff]Montando ficha e carregando miniaturas...", spinner="dots"):
        path.write_text(render(data),encoding="utf-8")
    webbrowser.open(path.resolve().as_uri())
    console.print(f"[green]✓ Ficha aberta[/green] [dim]{path}[/dim]")

def save_last(which):
    if which=="user" and LAST["user"]:
        p=LAST["user"]["profile"]; d=db.favorite("user",p["id"],p.get("name",""))
    elif which=="game" and LAST["game"]:
        p=LAST["game"]; d=db.favorite("game",(p.get("rootPlace") or {}).get("id"),p.get("name",""))
    elif which=="server" and LAST["servers"]:
        p=LAST["servers"][0]; d=db.favorite("server",p["id"],LAST["game"].get("name",""))
    else:
        console.print("[yellow]Não há resultado desse tipo para salvar.[/yellow]");return
    console.print("[green]✓ Favorito salvo:[/green] "+d["label"])

def case_wizard():
    console.print(Panel("[bold]Nova ocorrência[/bold]\n[dim]Registro manual e local. Não acusa nem rastreia usuários automaticamente.[/dim]",border_style=ACCENT))
    username=Prompt.ask("Username / ID")
    game=Prompt.ask("Jogo",default="")
    desc=Prompt.ask("Descrição da ocorrência")
    evidence=Prompt.ask("Link ou caminho da evidência",default="")
    value=db.create_case(username,game,desc,evidence)
    console.print("[green]✓ Ocorrência criada:[/green] "+value["id"])

def do_export(fmt):
    data=LAST["user"]
    if not data:
        console.print("[yellow]Consulte um usuário primeiro.[/yellow]");return
    ident=int(data["profile"]["id"])
    if fmt=="json":
        path=db.PROFILES/f"{ident}.json"
    elif fmt=="csv":
        path=db.export_csv(data)
    elif fmt=="html":
        open_card();return
    elif fmt=="pdf":
        from robloxdb_pdf import write_profile_pdf
        path=write_profile_pdf(data)
    else:
        console.print("[yellow]Use /export json, csv, html ou pdf.[/yellow]");return
    console.print("[green]✓ Arquivo disponível:[/green] "+str(path))

def run(initial_query=None):
    startup()
    if initial_query:
        try: get_user(initial_query)
        except (ValueError,db.APIError,OSError) as exc: console.print("[red]Erro:[/red]",str(exc))
    while True:
        try:
            raw=Prompt.ask("[bold #aabaff]robloxdb[/bold #aabaff] [dim]›[/dim]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Até mais.[/dim]");return 0
        if not raw: continue
        key,_,arg=raw.partition(" ")
        key=key.lower()
        try:
            if key in ("/exit","/quit","exit","quit"):return 0
            elif key in ("/help","help","?"):help_screen()
            elif key=="/clear":startup()
            elif key in ("/user","/search","/id"):get_user(arg)
            elif key=="/game":get_game(arg)
            elif key=="/servers":get_servers(arg)
            elif key=="/available":get_servers(available=True)
            elif key=="/presence":
                if not LAST["user"]:
                    console.print("[yellow]Consulte um usuário primeiro.[/yellow]")
                else:
                    uid = int(LAST["user"]["profile"]["id"])
                    with console.status("[#8fa5ff]Verificando presença...", spinner="dots"):
                        LAST["user"]["presence"] = db.check_presence(uid)
                        db.save_json(db.PROFILES / f"{uid}.json", LAST["user"])
                    status = LAST["user"]["presence"]
                    console.print("[bold]Presença:[/bold] " + str(status["status"])
                                  + " [dim](consulta de " + status["checked_at_utc"] + ")[/dim]")
            elif key=="/open":open_card()
            elif key=="/profile":
                if LAST["user"]:webbrowser.open("https://www.roblox.com/users/"+str(LAST["user"]["profile"]["id"])+"/profile")
                else:console.print("[yellow]Consulte um usuário primeiro.[/yellow]")
            elif key=="/join":
                if LAST["user"]:
                    console.print("[yellow]O Roblox controla a permissão de entrada na sessão.[/yellow]")
                    db.join_user(LAST["user"]["profile"]["id"])
                else:console.print("[yellow]Consulte um usuário primeiro.[/yellow]")
            elif key=="/save":save_last(arg.lower())
            elif key=="/favorites":table("FAVORITOS",["Tipo","ID","Nome"],[(x["kind"],x["id"],x["label"]) for x in db.favorites()])
            elif key=="/unsave":
                kind,_,ident=arg.partition(" ")
                console.print(f"[green]{db.remove_favorite(kind,ident)} favorito(s) removido(s).[/green]")
            elif key=="/history":table("HISTÓRICO",["Tipo","ID","Nome","Data"],[(x.get("kind"),x.get("id"),x.get("label"),x.get("at")) for x in db.history()])
            elif key=="/case":case_wizard()
            elif key=="/cases":table("OCORRÊNCIAS",["ID","Jogador","Jogo","Estado"],[(x["id"],x["username"],x["game"],x["status"]) for x in db.cases()])
            elif key=="/close":console.print("[green]✓ Ocorrência encerrada:[/green]", db.close_case(arg)["id"])
            elif key=="/compare":
                terms=arg.split()
                if len(terms)!=2:raise ValueError("Use /compare USER1 USER2")
                with console.status("Comparando perfis...",spinner="dots"):
                    a=db.lookup_user(terms[0]);b=db.lookup_user(terms[1])
                table("COMPARAÇÃO",["Campo",terms[0],terms[1]],db.compare_profiles(a,b))
            elif key=="/diagnose":table("DIAGNÓSTICO",["Serviço","Estado","Latência(ms)"],db.diagnostic())
            elif key=="/export":do_export(arg.lower())
            elif key=="/animations":
                if arg not in ("on","off"):raise ValueError("Use /animations on ou off")
                db.update_settings(animations=arg=="on")
                console.print("[green]✓ Preferência salva.[/green]")
            elif key.startswith("/"):console.print("[yellow]Comando desconhecido. Digite /help.[/yellow]")
            else:get_user(raw)
        except (ValueError,db.APIError,OSError,TypeError,KeyError) as exc:
            console.print("[red]Erro:[/red] "+str(exc).replace("[","(").replace("]",")"))
        except Exception as exc:
            console.print("[red]Falha inesperada:[/red] "+str(exc).replace("[","(").replace("]",")"))

if __name__=="__main__":
    raise SystemExit(run())
