"""Visual RobloxDB profile report with official public thumbnails."""
import html
import json
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request

def esc(value):
    return html.escape(str(value if value is not None else "Não disponível"), quote=True)

def thumbnails(path, ids, id_key, size="150x150"):
    ids = list(dict.fromkeys(str(i) for i in ids if str(i).isdigit() and int(i) > 0))[:100]
    result = {}
    for offset in range(0, len(ids), 50):
        chunk = ids[offset:offset + 50]
        url = "https://thumbnails.roblox.com" + path + "?" + urllib.parse.urlencode({
            id_key: ",".join(chunk), "size": size, "format": "Png"
        })
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "RobloxDB/0.4", "Accept": "application/json"})
            with urllib.request.urlopen(request, timeout=12) as response:
                body = json.load(response)
            for item in body.get("data", []):
                item_id = item.get("targetId")
                source = item.get("imageUrl")
                if isinstance(source, str) and source.startswith("https://"):
                    result[str(item_id)] = source
        except (urllib.error.URLError, TimeoutError, ValueError):
            continue
    return result

def game_id(game):
    try:
        return int(game.get("id") or 0)
    except (ValueError, TypeError):
        return 0

def game_place(game):
    try:
        return int((game.get("rootPlace") or {}).get("id") or 0)
    except (ValueError, TypeError):
        return 0

def game_cards(items, images):
    if not isinstance(items, list) or not items:
        return '<p class="empty">Nenhum jogo público disponível.</p>'
    output = []
    for game in items[:40]:
        uid = game_id(game)
        place = game_place(game)
        name = esc(game.get("name") or (game.get("rootPlace") or {}).get("name") or "Jogo")
        url = "https://www.roblox.com/games/" + str(place) if place else ""
        img = images.get(str(uid), "")
        thumb = '<img loading="lazy" alt="" src="' + esc(img) + '">' if img else '<div class="noimage">🎮</div>'
        content = '<div class="cover">' + thumb + '</div><div class="itemtitle">' + name + '</div>'
        if url:
            output.append('<a class="tile" href="' + esc(url) + '" target="_blank" rel="noopener noreferrer">' + content + '</a>')
        else:
            output.append('<div class="tile">' + content + '</div>')
    return '<div class="tiles">' + "".join(output) + '</div>'

def asset_cards(assets, images):
    if not isinstance(assets, list) or not assets:
        return '<p class="empty">Itens equipados indisponíveis.</p>'
    output = []
    for asset in assets[:40]:
        try:
            asset_id = int(asset)
        except (TypeError, ValueError):
            continue
        if asset_id <= 0:
            continue
        img = images.get(str(asset_id))
        thumb = '<img loading="lazy" alt="" src="' + esc(img) + '">' if img else '<div class="noimage">◇</div>'
        url = "https://www.roblox.com/catalog/" + str(asset_id)
        output.append('<a class="tile" href="' + url + '" target="_blank" rel="noopener noreferrer"><div class="cover">' + thumb + '</div><div class="itemtitle">Item #' + str(asset_id) + '</div></a>')
    return '<div class="tiles">' + "".join(output) + '</div>' if output else '<p class="empty">Itens não disponíveis.</p>'

def render(data):
    p = data["profile"]
    user_id = int(p["id"])
    counts = data.get("social_counts", {})
    favorites = data.get("favorite_games")
    creations = data.get("created_games")
    asset_ids = data.get("currently_wearing_asset_ids")
    allgames = [* (favorites or []), * (creations or [])]
    gameimages = thumbnails("/v1/games/icons", [game_id(g) for g in allgames], "universeIds", "150x150")
    assetimages = thumbnails("/v1/assets", asset_ids or [], "assetIds", "150x150")
    userimages = thumbnails("/v1/users/avatar-headshot", [user_id], "userIds", "150x150")
    avatar = userimages.get(str(user_id))
    avatar_html = '<img class="avatar" alt="Avatar Roblox" src="' + esc(avatar) + '">' if avatar else '<div class="avatar noimage">●</div>'
    presence = data.get("presence") or {}
    presence_label = presence.get("status", "Não verificado")
    presence_style = {"Online":"online","Jogando":"playing","No Studio":"studio",
                      "Offline":"offline"}.get(presence_label,"unknown")
    presence_html = '<span class="presence ' + presence_style + '">● ' + esc(presence_label) + '</span>'
    stats = "".join('<div class="stat"><strong>' + esc(counts.get(key)) + '</strong><span>' + label + '</span></div>' for key,label in (
        ("friends","Amigos"), ("followers","Seguidores"), ("following","Seguindo")))
    history = data.get("username_history")
    old_names = ", ".join(esc(x.get("name")) for x in history[:15] if isinstance(x, dict)) if isinstance(history, list) and history else "Não disponível"
    profile_url = "https://www.roblox.com/users/" + str(user_id) + "/profile"
    document = """<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>RobloxDB — __TITLE__</title>
<style>
:root{color-scheme:dark;--bg:#080b12;--panel:#121724;--line:#293245;--muted:#8997af;--accent:#859cff;--text:#f3f5ff}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:radial-gradient(ellipse 70% 30% at 50% -5%,#202c58 0%,transparent 75%),var(--bg);color:var(--text);font:15px/1.5 Inter,Segoe UI,system-ui,sans-serif}
header{position:sticky;top:0;z-index:5;background:#0b101bdc;backdrop-filter:blur(16px);border-bottom:1px solid var(--line)}
.bar{max-width:1150px;margin:auto;padding:15px 22px;display:flex;justify-content:space-between;align-items:center;gap:12px}
.logo{font-weight:850;font-size:17px;letter-spacing:.5px}.logo b{color:var(--accent)}.tag{color:var(--muted);font-size:12px}
main{max-width:1150px;margin:36px auto 70px;padding:0 22px}.panel{border:1px solid var(--line);background:linear-gradient(135deg,#151c2b,#111622);border-radius:20px;padding:25px;margin-bottom:23px;box-shadow:0 15px 35px #0002}
.hero{display:flex;align-items:center;gap:23px;flex-wrap:wrap}.avatar{width:122px;height:122px;object-fit:cover;border-radius:24px;background:#25304c;flex:none}.presence{display:inline-block;margin:0 0 10px;padding:6px 12px;border-radius:20px;background:#283247;color:#adb9d0;font-weight:750;font-size:13px}
.presence.online,.presence.playing{background:#123f32;color:#7ce3aa}.presence.studio{background:#163a4c;color:#8dd8ef}.presence.offline{background:#303540;color:#a6acb8}.presence.unknown{background:#4a3822;color:#f5c67e}
.hero h1{font-size:clamp(26px,4vw,42px);margin:0;line-height:1.2;overflow-wrap:anywhere}.handle{color:var(--muted);margin:7px 0 17px}
.btn{display:inline-flex;align-items:center;background:#7790ff;border:1px solid #9bafff;color:#081020;text-decoration:none;font-weight:800;border-radius:10px;padding:9px 15px}.btn:hover{background:#9cb0ff}.btn.join{background:#263350;border-color:#495e96;color:#c9d7ff;margin-left:6px}.btn.join:hover{background:#33466d}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:22px}.stat{border:1px solid #303a51;border-radius:14px;padding:15px;background:#1a2232;display:flex;flex-direction:column;align-items:center}.stat strong{font-size:26px}.stat span{font-size:12px;color:var(--muted)}
.descr{color:#c2cce1;white-space:pre-wrap;overflow-wrap:anywhere;margin:22px 0 0}
h2{font-size:19px;margin:0 0 16px}.sub{color:var(--muted);font-size:12px;font-weight:400;margin-left:8px}.tiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:14px}
.tile{min-width:0;color:inherit;text-decoration:none;border:1px solid #29364d;background:#1b2435;border-radius:13px;overflow:hidden;transition:transform .15s,border-color .15s}.tile:hover{transform:translateY(-3px);border-color:var(--accent)}
.cover{width:100%;aspect-ratio:1/1;background:#222d42}.cover img{width:100%;height:100%;object-fit:cover}.noimage{display:grid;place-items:center;color:#8294ba;font-size:34px;width:100%;height:100%}
.itemtitle{padding:10px 11px;font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.empty{color:var(--muted);margin:0}.info{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:18px}.info dt{font-size:12px;color:var(--muted)}.info dd{margin:3px 0 0;overflow-wrap:anywhere}
footer{color:var(--muted);font-size:12px;margin-top:26px}.quicknav{display:flex;flex-wrap:wrap;gap:9px;margin-bottom:22px}.quicknav a{color:#c6d5ff;background:#1a2439;border:1px solid #364563;border-radius:10px;padding:9px 13px;text-decoration:none;font-size:13px;transition:all .2s}.quicknav a:hover{background:#34476d;transform:translateY(-2px)}.panel{animation:rise .45s ease both}@keyframes rise{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}@media(prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important}}a{outline-offset:4px}
@media(max-width:540px){.panel{padding:17px}.hero{gap:15px}.avatar{width:85px;height:85px}.stats{gap:7px}.stat{padding:11px 4px}.stat strong{font-size:20px}.tiles{grid-template-columns:repeat(2,minmax(0,1fr))}.tag{display:none}}
</style></head><body>
<header><div class="bar"><div class="logo">ROBLOX<b>DB</b> <span class="tag">/ V2 PROFILE EXPLORER</span></div><div class="tag">PUBLIC DATA · V2.0</div></div></header>
<main><nav class="quicknav"><a href="#favorites">Favoritos</a><a href="#creations">Jogos criados</a><a href="#assets">Equipados</a><a href="#info">Conta</a></nav><section class="panel"><div class="hero">__AVATAR__<div><h1>__DISPLAY__</h1><div class="handle">@__NAME__ · ID __ID__</div>__PRESENCE__
<a class="btn" href="__PROFILE_URL__" target="_blank" rel="noopener noreferrer">Ver perfil Roblox ↗</a> <a class="btn join" href="__JOIN_URL__">▶ Entrar na partida</a></div></div>
<div class="stats">__STATS__</div><p class="descr">__DESCRIPTION__</p></section>
<section class="panel" id="favorites"><h2>★ Jogos favoritos <span class="sub">até 40 registros públicos</span></h2>__FAVORITES__</section>
<section class="panel" id="creations"><h2>▣ Jogos criados <span class="sub">até 40 registros públicos</span></h2>__CREATIONS__</section>
<section class="panel" id="assets"><h2>◇ Itens equipados <span class="sub">miniaturas de assets públicos</span></h2>__ASSETS__</section>
<section class="panel" id="info"><h2>Informações da conta</h2><dl class="info">
<div><dt>Criação</dt><dd>__CREATED__</dd></div><div><dt>Histórico de usernames</dt><dd>__HISTORY__</dd></div>
<div><dt>Visibilidade do inventário</dt><dd>__INVENTORY__</dd></div><div><dt>UserId</dt><dd>__ID__</dd></div></dl></section>
<footer>Consulta UTC: __TIMESTAMP__. Informações e imagens dependem dos endpoints públicos do Roblox. O status de presença é um instantâneo sujeito à privacidade e pode estar desatualizado. O inventário completo não é coletado. O botão de entrada só funciona se o Roblox permitir que você participe. RobloxDB não é afiliado ao Roblox.</footer></main></body></html>"""
    replacement = {
        "__TITLE__": esc(p.get("displayName") or p.get("name")),
        "__AVATAR__": avatar_html,
        "__DISPLAY__": esc(p.get("displayName") or p.get("name")),
        "__NAME__": esc(p.get("name")),
        "__ID__": str(user_id),
        "__PROFILE_URL__": esc(profile_url),
        "__PRESENCE__": presence_html,
        "__JOIN_URL__": esc("roblox://userId=" + str(user_id)),
        "__STATS__": stats,
        "__DESCRIPTION__": esc(p.get("description") or "Sem descrição pública."),
        "__FAVORITES__": game_cards(favorites, gameimages),
        "__CREATIONS__": game_cards(creations, gameimages),
        "__ASSETS__": asset_cards(asset_ids, assetimages),
        "__CREATED__": esc(p.get("created")),
        "__HISTORY__": old_names,
        "__INVENTORY__": esc(data.get("inventory_is_public")),
        "__TIMESTAMP__": esc(data.get("collected_at_utc")),
    }
    for token, value in replacement.items():
        document = document.replace(token, value)
    return document
