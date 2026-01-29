import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Ladda miljövariabler (.env)
load_dotenv()

client = None

def init():
    """Initierar bara klienten, behöver ingen dataframe"""
    global client
    api_key = os.getenv("GEMINI_API_KEY")
    
    if api_key:
        try:
            client = genai.Client(api_key=api_key)
            print("   [EXPLAINER] Redo att förklara resultat.")
        except Exception as e:
            print(f"   [EXPLAINER FEL] {e}")
    else:
        print("   [EXPLAINER] Ingen API-nyckel hittades.")

def enrich_results(query, recommendations):
    """
    Tar emot rå-resultat från TF-IDF/Hybrid och ber LLM förklara dem.
    """
    # Om klienten inte funkar eller listan är tom, returnera originalet direkt
    if not client or not recommendations:
        return recommendations

    try:
        # Hämta bara titlarna för att spara tid
        titles = [rec['title'] for rec in recommendations]
        
        prompt = f"""
        The user searched for: "{query}".
        My algorithm found these shows: {titles}.
        
        Task: Write a short, engaging 1-sentence reason (in English) for EACH show, explaining specifically why it fits the search "{query}".
        
        Return ONLY a JSON object mapping titles to reasons:
        {{
            "Show Title 1": "Reason 1...",
            "Show Title 2": "Reason 2..."
        }}
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        
        # Tolka svaret
        new_reasons = json.loads(response.text)
        
        # Uppdatera original-listan med de nya texterna
        for rec in recommendations:
            if rec['title'] in new_reasons:
                rec['reason'] = new_reasons[rec['title']]
                
        return recommendations

    except Exception as e:
        print(f"   [EXPLAINER ERROR] Kunde inte generera förklaringar: {e}")
        # Vid fel: Returnera originalen så användaren iaf får svar
        return recommendations