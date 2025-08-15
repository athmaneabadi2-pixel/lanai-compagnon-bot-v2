# lanai_memory.py
import json
from config import PROFILE_JSON_PATH

def load_profile():
    """Charge le profil de Mohamed depuis le fichier JSON et le retourne sous forme de dict."""
    try:
        with open(PROFILE_JSON_PATH, 'r', encoding='utf-8') as f:
            profile_data = json.load(f)
    except Exception as e:
        print(f"[ERREUR] Impossible de lire le fichier de profil {PROFILE_JSON_PATH}: {e}")
        profile_data = {}
    return profile_data

def format_profile_for_prompt(profile):
    """
    Formate certaines informations clés du profil en texte pour le prompt GPT.
    Retourne une chaîne de caractères (quelques phrases ou points).
    """
    if not profile:
        return ""

    identite = profile.get("Identité", {})
    famille = profile.get("Famille", {})
    gouts = profile.get("Goûts", {})
    souvenirs = profile.get("Souvenirs", {})
    bien_etre = profile.get("Bien-être", {})

    lines = []
    # Identité de base
    prenom = identite.get("Prénom", "Mohamed")
    age = identite.get("Âge")
    metier = identite.get("Métier exercé")
    if prenom and age:
        lines.append(f"{prenom}, {age}, ancien {metier.lower() if metier else 'professionnel'}.")

    # Santé
    sante = identite.get("Particularités de santé (Parkinson, etc.)") or identite.get("Particularités de santé")
    if sante:
        lines.append(f"Santé : {sante}.")

    # Famille
    epouse = famille.get("Nom de son épouse") or famille.get("Épouse")
    enfants = famille.get("Nom(s) et âge(s) des enfants") or famille.get("Enfants")
    if epouse:
        lines.append(f"Épouse : {epouse}.")
    if enfants:
        lines.append(f"Enfants : {enfants}.")

    # Centres d'intérêt
    sport_pref = gouts.get("Sport préféré")
    film_pref = gouts.get("Film ou série préférée")
    musique_pref = gouts.get("Musique/chanteur préféré")
    if sport_pref:
        lines.append(f"Passions : grand fan de {sport_pref.lower()}.")
    if film_pref:
        lines.append(f"Aime regarder : {film_pref}.")
    if musique_pref:
        lines.append(f"Aime écouter : {musique_pref}.")

    # Souvenirs / fiertés
    fierte = souvenirs.get("Fierté ou accomplissement") or souvenirs.get("Fierté")
    if fierte:
        lines.append(f"Fierté : {fierte}.")

    # Religion
    religion = identite.get("Religion")
    if religion:
        lines.append(f"Religion : {religion}.")

    # Bien-être / humeur
    humeur = bien_etre.get("Humeurs")
    if humeur:
        lines.append(f"Bien-être : {humeur}.")

    # Joindre le tout en une petite description
    profile_text = " ".join(lines)
    return profile_text
