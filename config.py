import os
from dotenv import load_dotenv

# Charger les variables depuis le fichier .env (en développement) 
# et depuis l'environnement système (en production sur Render)
load_dotenv()

# === Twilio (WhatsApp) ===
TWILIO_ACCOUNT_SID   = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN    = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_NUMBER")  # Numéro émetteur (WhatsApp Twilio)
TWILIO_WHATSAPP_TO   = os.getenv("MY_WHATSAPP_NUMBER")      # Numéro de Mohamed (destinataire)

# === API OpenAI (GPT-4) ===
OPENAI_API_KEY       = os.getenv("OPENAI_API_KEY")

# === API OpenWeather (Météo) ===
OPENWEATHER_API_KEY  = os.getenv("OPENWEATHER_API_KEY")

# === API Sports (via API-SPORTS/RapidAPI) ===
API_FOOT_KEY         = os.getenv("API_FOOT_KEY")    # Clé API pour le foot
API_BASKET_KEY       = os.getenv("API_BASKET_KEY")  # Clé API pour le basket

# === Autres paramètres ===
PROFILE_JSON_PATH    = os.getenv("PROFILE_JSON_PATH", "memoire_mohamed_lanai.json")
APP_TIMEZONE         = os.getenv("APP_TIMEZONE", "Europe/Paris")

# (Optionnel) Sécurité pour la route cron 
APP_JOBS_SECRET      = os.getenv("APP_JOBS_SECRET")  # Secret attendu pour /send_daily_message
