# lanai_weather.py
import requests
from config import OPENWEATHER_API_KEY

# Ville actuelle de Mohamed
DEFAULT_CITY = "Loffre,FR"

def get_weather(city: str = DEFAULT_CITY) -> str:
    """Retourne une phrase météo en français, sinon 'indisponible'."""
    if not OPENWEATHER_API_KEY:
        return "Météo : (clé API manquante)"
    try:
        url = ("https://api.openweathermap.org/data/2.5/weather"
               f"?q={city}&units=metric&lang=fr&appid={OPENWEATHER_API_KEY}")
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            return "Météo : (indisponible)"
        data = r.json()
        temp = data.get("main", {}).get("temp")
        desc = (data.get("weather") or [{}])[0].get("description")
        if temp is None or not desc:
            return "Météo : (indisponible)"
        return f"Il fait {round(temp)}°C avec {desc} à {city.split(',')[0]}."
    except Exception as e:
        print(f"[ERREUR] API météo : {e}")
        return "Météo : (indisponible)"
