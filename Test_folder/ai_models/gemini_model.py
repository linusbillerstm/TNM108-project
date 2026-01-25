import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = None
shows_context = []

def init(df):
    global client, shows_context
    # HÄR ÄR DIN NYCKEL (Jag tog den från din uppladdade fil)
    api_key = os.getenv("GEMINI_API_KEY")
    
    if api_key:
        client = genai.Client(api_key=api_key)
        shows_context = df[['title', 'year', 'genre', 'storyline', 'imdb_rating']].to_dict(orient='records')
        print("   [GEMINI] Redo.")
    else:
        print("   [GEMINI] Ingen API-nyckel hittades.")

def search(query, top_k=3):
    if not client:
        return [{"title": "Fel", "year": 0, "reason": "Gemini API-nyckel saknas.", "score": 0}]

    try:
        # Vi ber Gemini gissa hur bra matchningen är (Confidence Score)
        prompt = f"""
        Recommend {top_k} shows from this database based on: "{query}".
        Database: {json.dumps(shows_context)}
        
        Return JSON array: 
        [{{ "title": "...", "year": "...", "reason": "...", "score": 95, "rating": 0.1}}]
        
        Where 'score' is an integer (0-100) representing how well it fits the user request.
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        return json.loads(response.text)
    except Exception as e:
        return [{"title": "Error", "year": 0, "reason": str(e), "score": 0}]