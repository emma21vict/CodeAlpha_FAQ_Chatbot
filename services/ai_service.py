import os
import requests
import json

def generate_ai_response(incoming_msg, sender, user_settings, user_contacts, message_history):
    """
    Appelle l'API Google Gemini Pro directement via REST (requests) 
    pour éviter les bugs de la librairie google-generativeai sur Python 3.14.
    """
    api_key = os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        return "Erreur système: Clé API Gemini non configurée.", "Erreur Configuration"

    # 1. Construction du contexte global (instructions)
    system_instructions = f"""Tu es l'assistant virtuel (Chatbot) pour une entreprise.
Ton objectif est de répondre aux clients sur WhatsApp de façon concise et efficace.

INSTRUCTIONS SPÉCIFIQUES DÉFINIES PAR L'ENTREPRISE:
{user_settings.get('instructions', 'Réponds poliment aux questions.')}

TON/PERSONNALITÉ:
{user_settings.get('tone', 'Professionnel et courtois.')}

CONTACTS DE L'ENTREPRISE (à fournir si le client demande comment contacter un humain):
"""
    for contact in user_contacts:
        system_instructions += f"- {contact.name}: {contact.email} | {contact.phone}\n"
    
    system_instructions += "\nRÈGLE TRÈS IMPORTANTE : Ne dis JAMAIS que tu es une IA. Tu es l'assistant de l'entreprise. Réponds TOUJOURS de manière très concise (c'est un message WhatsApp)."

    # 2. Construction de l'historique au format attendu par Gemini
    contents = []
    for msg in message_history:
        contents.append({"role": "user", "parts": [{"text": msg.content}]})
        contents.append({"role": "model", "parts": [{"text": msg.reply}]})
        
    contents.append({"role": "user", "parts": [{"text": incoming_msg}]})

    # 3. Payload pour l'API REST
    payload = {
        "system_instruction": {
            "parts": [{"text": system_instructions}]
        },
        "contents": contents,
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 300,
        }
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Extraction de la réponse
        reply_text = data['candidates'][0]['content']['parts'][0]['text']
        usage = data.get('usageMetadata', {})
        total_tokens = usage.get('totalTokenCount', 'N/A')
        justification = f"Généré par gemini-1.5-pro (Tokens: {total_tokens})"
        
        return reply_text, justification
    except Exception as e:
        print(f"Erreur Gemini API: {e}")
        if 'response' in locals() and hasattr(response, 'text'):
            print(f"Détails: {response.text}")
        return "Désolé, je rencontre actuellement un problème technique. Veuillez réessayer plus tard.", "Erreur API Gemini"
