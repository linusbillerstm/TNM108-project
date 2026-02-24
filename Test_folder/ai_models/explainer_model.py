import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv


load_dotenv()

client = None

def init():
    global client
    api_key = os.getenv("GEMINI_API_KEY")
    
    if api_key:
        try:
            client = genai.Client(api_key=api_key)
            print("redo att förklara resultat.")
        except Exception as e:
            print(f"fel vid initiering av explainer {e}")
    else:
        print("explainer_model: Ingen API-nyckel hittades.")

def enrich_results(query, recommendations):
    """
    Tar emot resultat från TF-IDF/Hybrid och ber LLM förklara dem.
    """

    if not client or not recommendations:
        return recommendations

    try:
        # hämtar bara titlarna för att spara tid
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
        
        new_reasons = json.loads(response.text)
        
        # uppdatera med förklaringar
        for rec in recommendations:
            if rec['title'] in new_reasons:
                rec['reason'] = new_reasons[rec['title']]
                
        return recommendations

    except Exception as e:
        print(f"kunde inte generera förklaringar {e}")
        return recommendations