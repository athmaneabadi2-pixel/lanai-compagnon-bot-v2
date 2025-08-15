import openai
from config import OPENAI_API_KEY
from lanai_memory import format_profile_for_prompt

# Initialiser la clé API OpenAI
openai.api_key = OPENAI_API_KEY

# Un message système statique qui définit la personnalité et le ton de l'assistant Lanai
SYSTEM_PROMPT_TEMPLATE = (
    "Tu es Lanai, un assistant virtuel bienveillant créé pour accompagner Mohamed, un homme de 61 ans atteint de Parkinson. "
    "Tu t'exprimes en français de manière simple, chaleureuse et positive. "
    "Tu peux utiliser des expressions en arabe (ex: 'Salam aleykoum') de temps en temps pour saluer ou montrer de l'affection, car Mohamed est musulman pratiquant. "
    "Tu es toujours respectueux, amical, encourageant, et jamais froid ou trop formel. "
    "Tu disposes des informations suivantes sur Mohamed : {profile_info} "
    "Utilise-les pour personnaliser tes réponses *uniquement lorsque c'est pertinent*. "
    "N'inonde pas la conversation de détails non sollicités, mais sois attentif à ses besoins (santé, famille, goûts) lorsque tu formules tes réponses."
)

def generate_response(user_message, profile_data, extra_info_text=""):
    """
    Génère une réponse de Lanai à partir du message utilisateur, du profil et d'infos complémentaires.
    - user_message: texte du message de Mohamed
    - profile_data: dict avec les données profil de Mohamed
    - extra_info_text: chaîne optionnelle contenant des infos externes (météo, sport, etc.)
    """
    # Formater le profil en texte pour le prompt
    profile_text = format_profile_for_prompt(profile_data)
    # Préparer le contenu du message système en insérant le profil
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(profile_info=profile_text)

    # Construire la liste des messages pour l'API OpenAI
    messages = [
        {"role": "system", "content": system_prompt}
    ]

    # Si on a des infos externes (météo/sport), on peut les ajouter soit dans le system, soit en user
    if extra_info_text:
        # On ajoute les infos supplémentaires sous forme d'un message système ou user.
        # On choisit de l'ajouter dans le message utilisateur pour simuler qu'il fait partie du contexte de la question.
        user_content = f"{user_message}\n\n[Infos du jour]\n{extra_info_text}"
    else:
        user_content = user_message

    messages.append({"role": "user", "content": user_content})

    try:
        # Appel à l'API OpenAI pour GPT-4
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7  # on peut ajuster la créativité
        )
    except Exception as e:
        print(f"[ERREUR] Appel OpenAI échoué : {e}")
        return "Désolé, je ne peux pas répondre pour le moment."

    # Extraire le texte de la réponse
    answer = response["choices"][0]["message"]["content"].strip()
    return answer

def generate_daily_message(profile_data, extra_info_text=""):
    """
    Génère un message quotidien (bonjour du matin) en utilisant GPT-4.
    Combine le profil et des infos (météo/sport) pour créer un message spontané.
    """
    profile_text = format_profile_for_prompt(profile_data)
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(profile_info=profile_text)

    # Préparer une consigne utilisateur spéciale pour le message du jour
    daily_instruction = (
        "Ce matin, tu envoies à Mohamed un message pour prendre de ses nouvelles et lui apporter du réconfort. "
        "Inclue dans ton message la météo du jour et un fait sportif récent s'il y en a, de manière naturelle. "
        "Commence par le saluer chaleureusement. Ne dis pas que c'est un message automatique ou programmé."
    )
    # Si on a des infos externes à intégrer, on les ajoute après l'instruction
    if extra_info_text:
        daily_instruction += f"\n\n[Infos du jour]\n{extra_info_text}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": daily_instruction}
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.8  # on peut permettre un peu plus de créativité pour le message du matin
        )
    except Exception as e:
        print(f"[ERREUR] Appel OpenAI (daily) échoué : {e}")
        return "Salam aleykoum Mohamed ! (Message quotidien indisponible)"

    answer = response["choices"][0]["message"]["content"].strip()
    return answer
