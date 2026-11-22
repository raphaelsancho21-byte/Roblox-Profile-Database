"""RobloxDB V2 services: public APIs and local-first workspace."""
from __future__ import annotations
import csv
import datetime as datetime
import json
import os
from pathlib import Path
import re
import time
import urllib.parse
import urllib.request
import urllib.error
import webbrowser

from src.main import resolve, snapshot
from robloxdb_presence import check_presence

HOME = Path.home() / ".robloxdb"
PROFILES = HOME / "profiles"
REPORTS = HOME / "reports"
CASES = HOME / "cases"
FAV_FILE = HOME / "favorites.json"
HISTORY_FILE = HOME / "history.json"
SETTINGS_FILE = HOME / "settings.json"
URLS = {"games": "https://games.roblox.com", "users": "https://users.roblox.com",
        "universe": "https://apis.roblox.com", "thumbs": "https://thumbnails.roblox.com"}

class APIError(RuntimeError):
    pass

def stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")

def read_json(path, fallback):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return fallback

def save_json(path, payload):
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(dest)

def request(url, params=None):
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "RobloxDB-V2/2.0 (public discovery)", "Accept": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=12) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            if exc.code in (429,500,502,503,504) and attempt < 2:
                time.sleep(attempt + 1)
                continue
            raise APIError("Roblox retornou HTTP " + str(exc.code)) from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            if attempt < 2:
                time.sleep(attempt + 1)
                continue
            raise APIError("Sem conexão com a API Roblox") from exc
        except (ValueError, json.JSONDecodeError) as exc:
            raise APIError("Resposta da API inválida") from exc

def game_from_input(value):
    """Accept root place ID, a Roblox game URL or a numeric universe ID prefixed with u:."""
    value = value.strip()
    match = re.search(r"roblox\.com/games/(\d+)", value, re.I)
    if match:
        value = match.group(1)
    if value.lower().startswith("u:") and value[2:].isdigit():
        universe = int(value[2:])
        if universe <= 0:
            raise ValueError("UniverseId inválido")
        body = request(URLS["games"] + "/v1/games", {"universeIds": universe})
        data = body.get("data", [])
        if not data:
            raise APIError("Universe não localizado")
        return data[0]
    if not value.isdigit() or int(value) < 1:
        raise ValueError("Informe o PlaceId numérico ou link do jogo. Busca por nome não é confiável sem uma API pública estável.")
    place = int(value)
    body = request(URLS["universe"] + f"/universes/v1/places/{place}/universe")
    uid = body.get("universeId")
    if not uid:
        raise APIError("Não foi possível obter o UniverseId desse PlaceId")
    details = request(URLS["games"] + "/v1/games", {"universeIds": uid}).get("data", [])
    if not details:
        raise APIError("Detalhes do jogo indisponíveis")
    return details[0]

def lookup_user(query):
    key = query.strip().lstrip("@")
    if not key:
        raise ValueError("Digite um username ou UserId")
    uid = int(key) if key.isdigit() else resolve(key)
    if uid <= 0:
        raise ValueError("UserId inválido")
    data = snapshot(uid)
    data["presence"] = check_presence(uid)
    save_json(PROFILES / f"{uid}.json", data)
    add_history("profile", str(uid), data["profile"].get("name", str(uid)))
    return data

def get_profile_from_cache(query):
    p = PROFILES / (str(query) + ".json")
    result = read_json(p, None)
    return result if isinstance(result, dict) and "profile" in result else None

def game_servers(game, pages=1, sort="Asc", available_only=False):
    pages = max(1, min(5, int(pages)))
    place = (game.get("rootPlace") or {}).get("id")
    if not place:
        raise ValueError("PlaceId do jogo indisponível")
    next_cursor = None
    entries = []
    for _ in range(pages):
        params = {"limit": 100, "sortOrder": sort, "excludeFullGames": "true" if available_only else "false"}
        if next_cursor:
            params["cursor"] = next_cursor
        body = request(URLS["games"] + f"/v1/games/{int(place)}/servers/Public", params)
        entries.extend(body.get("data", []))
        next_cursor = body.get("nextPageCursor")
        if not next_cursor:
            break
    add_history("servers", str(place), game.get("name", str(place)))
    return entries, bool(next_cursor)

def add_history(kind, identifier, label):
    items = read_json(HISTORY_FILE, [])
    if not isinstance(items, list):
        items = []
    items.insert(0, {"kind": kind, "id": identifier, "label": label, "at": stamp()})
    save_json(HISTORY_FILE, items[:150])

def history(limit=20):
    return read_json(HISTORY_FILE, [])[:limit]

def favorite(kind, identifier, label):
    if kind not in ("user", "game", "server"):
        raise ValueError("Tipo de favorito inválido")
    records = read_json(FAV_FILE, [])
    if not isinstance(records, list):
        records = []
    record = {"kind": kind, "id": str(identifier), "label": label, "saved": stamp()}
    records = [r for r in records if (r.get("kind"), r.get("id")) != (record["kind"], record["id"])]
    records.insert(0, record)
    save_json(FAV_FILE, records[:150])
    return record

def favorites():
    return read_json(FAV_FILE, [])

def remove_favorite(kind, identifier):
    records = favorites()
    new = [r for r in records if (r.get("kind"), r.get("id")) != (kind, str(identifier))]
    save_json(FAV_FILE, new)
    return len(records) - len(new)

def create_case(username, game, description, evidence=""):
    username = username.strip()
    if not username or not description.strip():
        raise ValueError("Username e descrição são obrigatórios")
    case_id = datetime.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    payload = {"id": case_id, "username": username[:120], "game": game.strip()[:200],
               "description": description.strip()[:5000], "evidence": evidence.strip()[:1500],
               "created_at": stamp(), "status": "aberta"}
    save_json(CASES / f"{case_id}.json", payload)
    return payload

def cases():
    if not CASES.exists():
        return []
    return sorted([x for path in CASES.glob("*.json") if (x := read_json(path, None))], key=lambda x: x.get("created_at",""), reverse=True)

def close_case(case_id):
    if not re.fullmatch(r"[0-9]{8}-[0-9]{6}-[0-9]{6}", case_id):
        raise ValueError("ID de ocorrência inválido")
    path = CASES / f"{case_id}.json"
    data = read_json(path, None)
    if not data:
        raise ValueError("Ocorrência não encontrada")
    data["status"] = "fechada"
    data["closed_at"] = stamp()
    save_json(path, data)
    return data

def compare_profiles(a, b):
    ca = a.get("social_counts", {})
    cb = b.get("social_counts", {})
    return [(label, a["profile"].get(field), b["profile"].get(field)) for label,field in
            [("Username","name"),("DisplayName","displayName"),("Criação","created")]] + [
            (label, ca.get(field), cb.get(field)) for label,field in
            [("Amigos","friends"),("Seguidores","followers"),("Seguindo","following")]]

def diagnostic():
    results = []
    for label, url in [
        ("users", URLS["users"] + "/v1/users/1"),
        ("games", URLS["games"] + "/v1/games?universeIds=1"),
        ("thumbnails", URLS["thumbs"] + "/v1/users/avatar-headshot?userIds=1&size=150x150&format=Png")]:
        start = time.monotonic()
        try:
            request(url)
            results.append((label, "OK", round((time.monotonic() - start) * 1000)))
        except APIError as exc:
            results.append((label, str(exc), None))
    return results

def export_csv(data, filename=None):
    p = data["profile"]
    dest = REPORTS / (filename or f"profile-{p['id']}.csv")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["campo", "valor"])
        for k,v in p.items():
            writer.writerow([k, v])
        for k,v in data.get("social_counts", {}).items():
            writer.writerow(["social_" + k, v])
    return dest

def join_user(uid):
    if not str(uid).isdigit() or int(uid) <= 0:
        raise ValueError("UserId inválido")
    return webbrowser.open("roblox://userId=" + str(uid))

def open_game(place):
    if not str(place).isdigit() or int(place) <= 0:
        raise ValueError("PlaceId inválido")
    return webbrowser.open("https://www.roblox.com/games/" + str(place))

def settings():
    value = read_json(SETTINGS_FILE, {"animations": True, "server_pages": 1})
    if not isinstance(value, dict):
        return {"animations": True, "server_pages": 1}
    return value

def update_settings(**updates):
    current = settings()
    current.update(updates)
    save_json(SETTINGS_FILE, current)
    return current
