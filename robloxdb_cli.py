"""RobloxDB: lookup public Roblox profiles and open a local profile card."""
import argparse
import html
import json
from pathlib import Path
import sys
import webbrowser
from urllib.parse import quote

from src.main import snapshot, resolve

APP_DIR = Path.home() / ".robloxdb"
PROFILE_DIR = APP_DIR / "profiles"
CARD_DIR = APP_DIR / "cards"

def find_user(query):
    query = query.strip()
    if not query:
        raise ValueError("Informe um username ou UserId.")
    if query.isdecimal():
        n = int(query)
        if n <= 0:
            raise ValueError("UserId deve ser positivo.")
        return n
    return resolve(query.removeprefix("@"))

def thumbnail(user_id):
    # No cookies or private endpoints. Falls back to Roblox placeholder.
    import urllib.request
    url = "https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds=" + str(user_id) + "&size=150x150&format=Png&isCircular=false"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "RobloxDB/0.2", "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.load(response)
        items = data.get("data", [])
        if items:
            candidate = items[0].get("imageUrl", "")
            if candidate.startswith("https://"):
                return candidate
    except Exception:
        pass
    return ""

def safe(value):
    return html.escape(str(value)) if value is not None else "Não disponível"

def game_list(entries):
    if not isinstance(entries, list) or not entries:
        return '<p class="muted">Nenhuma informação pública disponível.</p>'
    parts = []
    for entry in entries[:50]:
        detail = entry.get("rootPlace") or {}
        name = entry.get("name") or detail.get("name") or "Jogo"
        place_id = detail.get("id")
        link = ("https://www.roblox.com/games/" + str(int(place_id))) if isinstance(place_id, int) and place_id > 0 else ""
        if link:
            parts.append('<a class="game" target="_blank" rel="noopener noreferrer" href="' + html.escape(link, quote=True) + '">' + safe(name) + '</a>')
        else:
            parts.append('<span class="game">' + safe(name) + '</span>')
    return "\n".join(parts)

def card(data):
    p = data["profile"]
    user_id = int(p["id"])
    avatar = thumbnail(user_id)
    image = '<img class="avatar" alt="Avatar" src="' + html.escape(avatar, quote=True) + '">' if avatar else '<div class="avatar placeholder">R</div>'
    counts = data["social_counts"]
    stats = "".join('<div class="stat"><b>' + safe(counts.get(k)) + '</b><span>' + label + '</span></div>' for k, label in (
        ("friends", "Amigos"), ("followers", "Seguidores"), ("following", "Seguindo")))
    username_history = data.get("username_history")
    previous = ", ".join(safe(x.get("name", "")) for x in username_history[:30]) if isinstance(username_history, list) and username_history else "Não disponível"
    equipment = data.get("currently_wearing_asset_ids")
    equipment_text = ", ".join(str(x) for x in equipment) if isinstance(equipment, list) else "Não disponível"
    profile_url = "https://www.roblox.com/users/" + str(user_id) + "/profile"
    return """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>RobloxDB · """ + safe(p.get("displayName") or p.get("name")) + """</title>
<style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#0b0d13;color:#edf0f7;font:15px system-ui,Segoe UI,Arial,sans-serif}
.wrap{max-width:980px;margin:42px auto;padding:0 20px}.brand{font-size:14px;color:#8ea4ff;font-weight:800;letter-spacing:2px}
.panel{background:#151924;border:1px solid #292f40;border-radius:20px;padding:30px;margin-top:18px;box-shadow:0 16px 46px #0005}
.hero{display:flex;gap:23px;align-items:center;flex-wrap:wrap}.avatar{width:112px;height:112px;object-fit:cover;border-radius:22px;background:#293048}
.placeholder{display:grid;place-items:center;font-size:52px}h1{margin:0;font-size:34px}h2{margin:0 0 18px;font-size:19px}.muted,.handle{color:#a0abc1}.handle{margin:5px 0 12px}
a{color:#9fb4ff}.button{display:inline-block;padding:10px 16px;border-radius:9px;text-decoration:none;background:#5067de;color:white;font-weight:650}
.stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin-top:24px}.stat{padding:16px;background:#1d2331;border-radius:12px;text-align:center;display:grid;gap:5px}
.stat b{font-size:25px}.stat span{font-size:12px;color:#9baac4}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}.grid .panel{margin-top:18px}
.game{display:block;padding:10px 12px;margin-bottom:7px;border-radius:9px;background:#202639;text-decoration:none;color:#edf0f7;overflow-wrap:anywhere}
.game:hover{background:#293757}.meta{overflow-wrap:anywhere;line-height:1.7}footer{margin:25px 0 40px;color:#8390aa;font-size:12px}
@media(max-width:650px){.grid{grid-template-columns:1fr}.stats{grid-template-columns:repeat(3,1fr)}.panel{padding:20px}.stat{padding:10px}.stat b{font-size:18px}h1{font-size:26px}}
</style></head><body><main class="wrap"><div class="brand">ROBLOXDB / PUBLIC PROFILE</div>
<section class="panel"><div class="hero">""" + image + """<div><h1>""" + safe(p.get("displayName")) + """</h1><div class="handle">@""" + safe(p.get("name")) + """ · ID """ + safe(user_id) + """</div><a class="button" target="_blank" rel="noopener noreferrer" href="""" + profile_url + """">Abrir no Roblox</a></div></div>
<div class="stats">""" + stats + """</div><p class="meta">""" + safe(p.get("description") or "Sem descrição pública.") + """</p></section>
<div class="grid"><section class="panel"><h2>Jogos favoritos</h2>""" + game_list(data.get("favorite_games")) + """</section>
<section class="panel"><h2>Jogos criados</h2>""" + game_list(data.get("created_games")) + """</section>
<section class="panel"><h2>Informações</h2><p class="meta">Criado em: """ + safe(p.get("created")) + """<br>Username anterior: """ + previous + """<br>Inventário visível: """ + safe(data.get("inventory_is_public")) + """</p></section>
<section class="panel"><h2>Itens equipados</h2><p class="meta">IDs de assets: """ + safe(equipment_text) + """</p></section></div>
<footer>Última consulta UTC: """ + safe(data.get("collected_at_utc")) + """. Dados públicos; partes podem estar ocultas ou indisponíveis. Ficha local gerada por RobloxDB.</footer></main></body></html>"""

def display_terminal(data):
    p = data["profile"]
    c = data["social_counts"]
    print("\n" + "=" * 52)
    print("  ROBLOXDB  |  FICHA PÚBLICA")
    print("=" * 52)
    print("  Nome:       " + str(p.get("displayName", "?")))
    print("  Username:   @" + str(p.get("name", "?")))
    print("  UserId:     " + str(p.get("id", "?")))
    print("  Criado em:  " + str(p.get("created", "?")))
    print("  Amigos:     " + str(c.get("friends")))
    print("  Seguidores: " + str(c.get("followers")))
    print("  Seguindo:   " + str(c.get("following")))
    print("  Favoritos:  " + str(len(data["favorite_games"])) if isinstance(data["favorite_games"], list) else "  Favoritos:  Não disponível")
    print("=" * 52)

def main():
    parser = argparse.ArgumentParser(prog="robloxdb", description="Abre uma ficha pública de perfil Roblox no navegador.")
    parser.add_argument("user", nargs="?", help="Username ou UserId Roblox")
    parser.add_argument("--terminal", action="store_true", help="Mostrar somente no CMD")
    parser.add_argument("--no-open", action="store_true", help="Gerar HTML sem abrir navegador")
    args = parser.parse_args()
    try:
        query = args.user or input("RobloxDB | Digite o username ou UserId: ")
        user_id = find_user(query)
        print("Consultando perfil público...")
        data = snapshot(user_id)
        PROFILE_DIR.mkdir(parents=True, exist_ok=True)
        CARD_DIR.mkdir(parents=True, exist_ok=True)
        json_path = PROFILE_DIR / (str(user_id) + ".json")
        html_path = CARD_DIR / (str(user_id) + ".html")
        json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        if args.terminal:
            display_terminal(data)
        else:
            html_path.write_text(card(data), encoding="utf-8")
            display_terminal(data)
            if not args.no_open:
                webbrowser.open(html_path.resolve().as_uri())
                print("\nFicha aberta no navegador.")
            print("Ficha HTML: " + str(html_path))
        print("JSON salvo: " + str(json_path))
    except (ValueError, KeyboardInterrupt, EOFError) as ex:
        print("\nErro: " + (str(ex) or "Operação cancelada."), file=sys.stderr)
        return 1
    except Exception as ex:
        print("Falha na consulta: " + str(ex), file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
