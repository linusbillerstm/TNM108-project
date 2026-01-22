# ai_models/router_agent.py
import json
from google.genai import types

def detect_intent(client, user_message):
    """
    Analyserar om användaren vill söka baserat på beskrivning 
    eller baserat på tidigare historik.
    """
    system_instruction = """
    You are an intent classifier. Analyze the user's message.
    Determine if they are asking for recommendations based on their 
    PAST HISTORY/TASTE (e.g., "What should I watch?", "Recommend something for me", "Something similar to what I like")
    OR if they are describing a SPECIFIC TOPIC/GENRE (e.g., "Show about space", "Funny sitcoms", "Something with dragons").
    
    Output strictly JSON: {"intent": "history"} OR {"intent": "description"}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", # Flash är snabb och billig för detta
            contents=[user_message],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.0, # Vi vill ha exakta svar, ingen kreativitet
                response_mime_type="application/json"
            )
        )
        result = json.loads(response.text)
        return result.get("intent", "description") # Fallback till description om osäker
    except:
        return "description"