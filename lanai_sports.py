# lanai_sports.py
import requests
from datetime import datetime
from config import API_FOOT_KEY, API_BASKET_KEY

FOOT_BASE = "https://v3.football.api-sports.io"
BASKET_BASE = "https://v1.basketball.api-sports.io"

# Petites normalisations pour comprendre "psg", "lakers", etc.
ALIASES_FOOT = {
    "psg": "paris saint-germain",
    "paris": "paris saint-germain",
}
ALIASES_BASKET = {
    "lakers": "los angeles lakers",
    "los angeles": "los angeles lakers",
    "la lakers": "los angeles lakers",
}

def _api(url, headers, params=None):
    try:
        r = requests.get(url, headers=headers, params=params or {}, timeout=12)
        if r.status_code != 200:
            print(f"[WARN] {url} -> {r.status_code} {r.text[:120]}")
            return None
        return r.json()
    except Exception as e:
        print(f"[WARN] call failed {url}: {e}")
        return None

# ---------- FOOT ----------
def _foot_headers():
    return {"x-apisports-key": API_FOOT_KEY} if API_FOOT_KEY else None

def _foot_find_team_id(name_query: str):
    if not _foot_headers():
        return None
    q = name_query.strip().lower()
    q = ALIASES_FOOT.get(q, q)
    data = _api(f"{FOOT_BASE}/teams", _foot_headers(), {"search": q})
    if not data:
        return None
    resp = data.get("response", [])
    return resp[0]["team"]["id"] if resp else None

def foot_next_game(team_query: str):
    tid = _foot_find_team_id(team_query)
    if not tid:
        return ""
    data = _api(f"{FOOT_BASE}/fixtures", _foot_headers(), {"team": tid, "next": 1})
    if not data or not data.get("response"):
        return "Je n'ai pas trouvé le prochain match."
    f = data["response"][0]
    home = f["teams"]["home"]["name"]; away = f["teams"]["away"]["name"]
    date_iso = f["fixture"]["date"]; date_str = _format_date(date_iso)
    league = f["league"]["name"]
    return f"Prochain match {league} : {home} vs {away}, le {date_str}."

def foot_last_result(team_query: str):
    tid = _foot_find_team_id(team_query)
    if not tid:
        return ""
    data = _api(f"{FOOT_BASE}/fixtures", _foot_headers(), {"team": tid, "last": 1})
    if not data or not data.get("response"):
        return "Je n'ai pas trouvé le dernier résultat."
    f = data["response"][0]
    home = f["teams"]["home"]["name"]; away = f["teams"]["away"]["name"]
    sh = f["goals"]["home"]; sa = f["goals"]["away"]
    league = f["league"]["name"]
    date_iso = f["fixture"]["date"]; date_str = _format_date(date_iso)
    return f"Dernier résultat {league} ({date_str}) : {home} {sh} - {sa} {away}."

# ---------- BASKET ----------
def _basket_headers():
    return {"x-apisports-key": API_BASKET_KEY} if API_BASKET_KEY else None

def _basket_find_team_id(name_query: str):
    if not _basket_headers():
        return None
    q = name_query.strip().lower()
    q = ALIASES_BASKET.get(q, q)
    data = _api(f"{BASKET_BASE}/teams", _basket_headers(), {"search": q})
    if not data:
        return None
    resp = data.get("response", [])
    return resp[0]["id"] if resp else None

def basket_next_game(team_query: str):
    tid = _basket_find_team_id(team_query)
    if not tid:
        return ""
    data = _api(f"{BASKET_BASE}/games", _basket_headers(), {"team": tid, "next": 1})
    if not data or not data.get("response"):
        return "Je n'ai pas trouvé le prochain match."
    g = data["response"][0]
    home = g["teams"]["home"]["name"]; away = g["teams"]["away"]["name"]
    date_iso = g["date"]; date_str = _format_date(date_iso)
    league = g["league"]["name"]
    return f"Prochain match {league} : {home} vs {away}, le {date_str}."

def basket_last_result(team_query: str):
    tid = _basket_find_team_id(team_query)
    if not tid:
        return ""
    data = _api(f"{BASKET_BASE}/games", _basket_headers(), {"team": tid, "last": 1})
    if not data or not data.get("response"):
        return "Je n'ai pas trouvé le dernier résultat."
    g = data["response"][0]
    home = g["teams"]["home"]["name"]; away = g["teams"]["away"]["name"]
    sh = g["scores"]["home"]["points"]; sa = g["scores"]["away"]["points"]
    date_iso = g["date"]; date_str = _format_date(date_iso)
    league = g["league"]["name"]
    return f"Dernier résultat {league} ({date_str}) : {home} {sh} - {sa} {away}."

# ---------- Résumé d'hier (on garde au cas où) ----------
def get_latest_results() -> str:
    # Gardé pour le message quotidien et les demandes génériques
    return ""

# ---------- Utilitaires ----------
def _format_date(date_iso: str) -> str:
    try:
        # API-SPORTS renvoie souvent un ISO : parse -> format FR
        dt = datetime.fromisoformat(date_iso.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y à %Hh%M")
    except Exception:
        return date_iso
