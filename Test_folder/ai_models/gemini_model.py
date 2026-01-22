import os
import json
from google import genai
from google.genai import types

client = None
shows_context = []

def init(df):
    global client, shows_context
    # Hämta API-nyckeln från miljövariabel
    api_key = os.environ.get("AIzaSyBNVnoRHvXyIgLb90Odx66sbV91ngN9I8I")
    
    if api_key:
        client = genai.Client(api_key=api_key)
        # Förbered datan för prompten
        shows_context = df[['title', 'year', 'genre', 'storyline']].to_dict(orient='records')
        print("   [GEMINI] Redo.")
    else:
        print("   [GEMINI] Ingen API-nyckel hittades.")

def search(query, top_k=3):
    if not client:
        return [{"title": "Fel", "year": 0, "reason": "Gemini API-nyckel saknas."}]

    try:
        # Prompten skickar med hela databasen som text
        prompt = f"""
        Recommend {top_k} shows from this database based on: "{query}".
        Database: {json.dumps(shows_context)}
        Return JSON array: [{{ "title": "...", "year": "...", "reason": "..." }}]
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
    except Exception as e:
        return [{"title": "Error", "year": 0, "reason": str(e)}]