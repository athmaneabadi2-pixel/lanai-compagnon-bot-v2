# lanai_sports.py
import requests
from datetime import datetime, timedelta
from config import API_FOOT_KEY, API_BASKET_KEY

# --- Ligues à suivre (API-SPORTS) ---
# Football (v3.football.api-sports.io)
COMPETITIONS_FOOT = {
    "Ligue 1": 61,              # France - Ligue 1
    "Ligue des Champions": 2,   # UEFA Champions League
    # Remarque : l'équipe de France n'est pas une "league".
    # On reste sur ligues majeures pour la robustesse.
}

# Basket (v1.basketball.api-sports.io)
COMPETITIONS_BASKET = {
    "NBA": 12,        # NBA
    "LNB Pro A": 2    # France Pro A (peut être 2/87 selon les versions d'API-Sports)
}

def _call_api(url: str, headers: dict, params: dict) -> dict | None:
    try:
        r = requests.get(url, headers=headers, params=params, timeout=12)
        if r.status_code != 200:
            print(f"[WARN] {url} -> {r.status_code} {r.text[:120]}")
            return None
        return r.json()
    except Exception as e:
        print(f"[WARN] API call failed {url}: {e}")
        return None

def get_latest_results() -> str:
    """
    Renvoie un bloc texte lisible avec les résultats d'hier (foot + basket).
    Utilise directement API-SPORTS (pas RapidAPI).
    """
    lines = []
    y = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    # --- FOOT ---
    if API_FOOT_KEY:
        headers_foot = {"x-apisports-key": API_FOOT_KEY}
        base_foot = "https://v3.football.api-sports.io/fixtures"
        for name, league_id in COMPETITIONS_FOOT.items():
            data = _call_api(
                base_foot,
                headers_foot,
                {"date": y, "league": league_id, "season": 2024}
            )
            if not data:
                continue
            for m in data.get("response", []):
                try:
                    home = m["teams"]["home"]["name"]
                    away = m["teams"]["away"]["name"]
                    sh = m["goals"]["home"]
                    sa = m["goals"]["away"]
                    if sh is None or sa is None:
                        # match pas encore joué / reporté
                        continue
                    lines.append(f"[{name}] {home} {sh} - {sa} {away}")
                except Exception:
                    continue

    # --- BASKET ---
    if API_BASKET_KEY:
        headers_basket = {"x-apisports-key": API_BASKET_KEY}
        base_basket = "https://v1.basketball.api-sports.io/games"
        for name, league_id in COMPETITIONS_BASKET.items():
            data = _call_api(
                base_basket,
                headers_basket,
                {"date": y, "league": league_id, "season": 2024}
            )
            if not data:
                continue
            for g in data.get("response", []):
                try:
                    home = g["teams"]["home"]["name"]
                    away = g["teams"]["away"]["name"]
                    sh = g["scores"]["home"]["points"]
                    sa = g["scores"]["away"]["points"]
                    if sh is None or sa is None:
                        continue
                    lines.append(f"[{name}] {home} {sh} - {sa} {away}")
                except Exception:
                    continue

    return "" if not lines else f"Résultats du {y} :\n" + "\n".join(lines)
