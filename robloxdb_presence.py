"""Public Roblox presence, respecting unavailable or restricted responses."""
import datetime as dt
import json
import time
import urllib.error
import urllib.request

ENDPOINT = "https://presence.roblox.com/v1/presence/users"
LABELS = {0: "Offline segundo API", 1: "Online", 2: "Jogando", 3: "No Studio", 4: "Indisponível"}

def check_presence(user_id):
    """One-shot public presence query. Never infer offline from an API error."""
    user_id = int(user_id)
    if user_id <= 0:
        raise ValueError("UserId inválido")
    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps({"userIds": [user_id]}).encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json", "Accept": "application/json",
                 "User-Agent": "RobloxDB/2.1 (public profile lookup)"})
    timestamp = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=12) as response:
                body = json.load(response)
            presences = body.get("userPresences", [])
            entry = next((x for x in presences if x.get("userId") == user_id), None)
            if not entry:
                return {"status": "Indisponível", "type": None,
                        "reason": "Presença não retornada pela API", "checked_at_utc": timestamp}
            presence_type = entry.get("userPresenceType")
            if type(presence_type) is not int:
                presence_type = None
            if presence_type not in LABELS:
                presence_type = None
            label = LABELS.get(presence_type, "Indisponível")
            # Never store last location, server IDs or private activity metadata.
            return {"status": label, "type": presence_type,
                    "reason": ("O Roblox reportou offline, mas a privacidade ou uma divergência pode ocultar a atividade real" if presence_type == 0 else "Visibilidade pode ser limitada por privacidade" if presence_type == 4 else None),
                    "checked_at_utc": timestamp}
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(attempt + 1)
                continue
            return {"status": "Indisponível", "type": None,
                    "reason": f"API retornou HTTP {exc.code}", "checked_at_utc": timestamp}
        except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            if attempt < 2:
                time.sleep(attempt + 1)
                continue
            return {"status": "Indisponível", "type": None,
                    "reason": "Falha de conexão ou resposta inválida", "checked_at_utc": timestamp}
    return {"status": "Indisponível", "type": None,
            "reason": "Não foi possível verificar", "checked_at_utc": timestamp}
