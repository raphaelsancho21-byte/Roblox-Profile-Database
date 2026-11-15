#!/usr/bin/env python3
"""Roblox public profile snapshot collector. No login or cookies."""
import argparse
import datetime as dt
import json
from pathlib import Path
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = {
    'users': 'https://users.roblox.com',
    'friends': 'https://friends.roblox.com',
    'games': 'https://games.roblox.com',
    'avatar': 'https://avatar.roblox.com',
    'inventory': 'https://inventory.roblox.com',
}

def get(base, path, params=None):
    url = BASE[base] + path
    if params:
        url += '?' + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        'User-Agent': 'RobloxProfileDatabase/0.1 (public profile research)',
        'Accept': 'application/json',
    })
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=15) as response:
                return json.load(response)
        except urllib.error.HTTPError as ex:
            if ex.code in (401, 403, 404):
                return {'_unavailable': f'HTTP {ex.code}'}
            if ex.code == 429 or ex.code >= 500:
                if attempt < 2:
                    time.sleep(2 ** attempt + 1)
                    continue
            return {'_unavailable': f'HTTP {ex.code}'}
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as ex:
            if attempt < 2:
                time.sleep(2 ** attempt + 1)
                continue
            return {'_unavailable': type(ex).__name__}
    return {'_unavailable': 'Unknown error'}

def resolve(name):
    # Public username search; exact case-insensitive match only.
    data = get('users', '/v1/users/search', {'keyword': name, 'limit': 50})
    matches = data.get('data', []) if isinstance(data, dict) else []
    for item in matches:
        if item.get('name', '').casefold() == name.casefold():
            return item['id']
    raise ValueError('Username exato não encontrado; use --id para maior precisão.')

def snapshot(user_id):
    p = f'/v1/users/{user_id}'
    profile = get('users', p)
    if 'id' not in profile:
        raise ValueError(f'Perfil não encontrado ou indisponível: {profile}')
    counts = {
        'friends': get('friends', f'{p}/friends/count').get('count'),
        'followers': get('friends', f'{p}/followers/count').get('count'),
        'following': get('friends', f'{p}/followings/count').get('count'),
    }
    favorites = get('games', f'/v2/users/{user_id}/favorite/games', {'limit': 50, 'sortOrder': 'Asc'})
    created_games = get('games', f'/v2/users/{user_id}/games', {'limit': 50, 'sortOrder': 'Asc'})
    equipped = get('avatar', f'/v1/users/{user_id}/currently-wearing')
    inventory_visibility = get('inventory', f'/v1/users/{user_id}/can-view-inventory')
    usernames = get('users', f'{p}/username-history', {'limit': 50, 'sortOrder': 'Desc'})
    return {
        'schema_version': 1,
        'collected_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'source': 'Roblox public endpoints; no authenticated session',
        'profile': {k: profile.get(k) for k in ('id', 'name', 'displayName', 'description', 'created', 'isBanned', 'hasVerifiedBadge') if k in profile},
        'social_counts': counts,
        'favorite_games': favorites.get('data') if isinstance(favorites, dict) else None,
        'created_games': created_games.get('data') if isinstance(created_games, dict) else None,
        'currently_wearing_asset_ids': equipped.get('assetIds') if isinstance(equipped, dict) else None,
        'inventory_is_public': inventory_visibility.get('canView') if isinstance(inventory_visibility, dict) else None,
        'username_history': usernames.get('data') if isinstance(usernames, dict) else None,
        'notes': 'Ausência de campo não significa zero; endpoints podem exigir autenticação ou ser limitados.',
    }

def main():
    parser = argparse.ArgumentParser(description='Consulta pública de perfil Roblox')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--id', type=int, help='Roblox UserId')
    group.add_argument('--username', help='Username exato')
    parser.add_argument('--out', default='data/profiles', help='Pasta de saída')
    args = parser.parse_args()
    user_id = args.id if args.id is not None else resolve(args.username)
    if user_id <= 0:
        parser.error('UserId deve ser positivo')
    data = snapshot(user_id)
    dest = Path(args.out)
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / f'{user_id}.json'
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Perfil salvo: {path}')

if __name__ == '__main__':
    main()
