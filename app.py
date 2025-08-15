from flask import Flask, request, Response
from twilio.rest import Client

from config import (
    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN,
    TWILIO_WHATSAPP_FROM, TWILIO_WHATSAPP_TO,
    APP_JOBS_SECRET
)
from lanai_memory import load_profile
from lanai_openai import generate_response, generate_daily_message
from lanai_weather import get_weather
from lanai_sports import get_latest_results

app = Flask(__name__)
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    """Reçoit les messages WhatsApp via Twilio, appelle GPT-4 et répond."""
    incoming_msg = (request.values.get("Body") or "").strip()
    sender = request.values.get("From")  # ex: "whatsapp:+33..."
    print(f"[Webhook] {sender} -> {incoming_msg}")

    if not incoming_msg or not sender:
        return Response(status=204)

    # 1) lire le profil JSON
    profile = load_profile()

       # 2) préparer infos externes si utiles
    extra = ""
    low = incoming_msg.lower()

    # Météo
    if any(w in low for w in ["météo", "meteo", "temps"]):
        extra += get_weather() + "\n"

    # Sports : compréhension simple d'intention + équipe
    from lanai_sports import (
        foot_next_game, foot_last_result,
        basket_next_game, basket_last_result,
        get_latest_results
    )

    # Team hints
    team = None
    is_next = any(w in low for w in ["prochain", "prochaine", "next"])
    is_last = any(w in low for w in ["dernier", "dernière", "resultat", "résultat"])

    if "psg" in low or "paris" in low:
        team = "psg"
        if is_next:
            extra += foot_next_game(team) or ""
        elif is_last or "score" in low:
            extra += foot_last_result(team) or ""
    elif "lakers" in low or "los angeles" in low:
        team = "lakers"
        if is_next:
            extra += basket_next_game(team) or ""
        elif is_last or "score" in low:
            extra += basket_last_result(team) or ""

    # Si demande sport générique (sans équipe), on peut mettre un résumé (optionnel)
    if not team and any(w in low for w in ["score", "match", "résultat", "resultat", "basket", "foot", "nba", "ligue 1"]):
        extra += get_latest_results() or ""


    # 3) demander la réponse à GPT‑4
    answer = generate_response(incoming_msg, profile, extra_info_text=extra)

    # 4) envoyer la réponse via Twilio
    try:
        msg = twilio_client.messages.create(
            body=answer,
            from_=TWILIO_WHATSAPP_FROM,
            to=sender
        )
        print(f"[Twilio] envoyé SID={msg.sid}")
    except Exception as e:
        print(f"[ERREUR] Envoi Twilio: {e}")

    return Response(status=200)

@app.route("/send_daily_message", methods=["GET"])
def send_daily_message():
    """Route appelée par ton cron externe pour le message du matin."""
    secret = request.args.get("secret")
    if APP_JOBS_SECRET and secret != APP_JOBS_SECRET:
        return Response("Unauthorized", status=401)

    profile = load_profile()
    extra = get_weather()
    sports = get_latest_results()
    if sports:
        extra += "\n" + sports

    daily = generate_daily_message(profile, extra_info_text=extra)

    try:
        msg = twilio_client.messages.create(
            body=daily,
            from_=TWILIO_WHATSAPP_FROM,
            to=TWILIO_WHATSAPP_TO
        )
        print(f"[Cron] quotidien envoyé SID={msg.sid}")
        return Response("OK", status=200)
    except Exception as e:
        print(f"[ERREUR] Envoi quotidien: {e}")
        return Response("KO", status=500)

if __name__ == "__main__":
    # utile en local, Render utilisera gunicorn
    app.run(host="0.0.0.0", port=5000)
