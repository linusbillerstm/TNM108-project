import pandas as pd
import os
import time
import random
from flask import Flask, render_template, request, jsonify

# --- IMPORTERA DINA NYA MODELLER ---
from ai_models import tfidf_model, nomic_model, gemini_model, hybrid_model, explainer_model

# --- FIX 1: Ändra så Flask hittar CSS/JS i samma mapp ---
app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')

# --- INITIERING AV AI (Körs en gång vid start) ---
def start_app():
    print("⏳ Laddar dataset och AI-modeller...")
    try:
        # 1. Läs in CSV-filen
        base_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(base_dir, 'sorted_shows.csv')
        df = pd.read_csv(csv_path)     
        
        # Säkerställ att inga NaNs finns kvar
        df['combined_text'] = df['combined_text'].fillna('') 
        
        # 2. Skicka datan till varje modell
        tfidf_model.init(df)
        nomic_model.init(df)
        gemini_model.init(df)
        hybrid_model.init(df)
        
        explainer_model.init()

        print("✅ Allt laddat och klart!")
    except Exception as e:
        # Skriv ut mer detaljerat felmeddelande
        print(f"❌ Kritiskt fel vid start av AI-modeller: {e}")
        import traceback
        traceback.print_exc()

# Kör initieringen direkt
with app.app_context():
    start_app()

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    selected_model = data.get('model', 'tfidf')
    
    recommendations = []
    intro = ""

    if selected_model == "tfidf":
        intro = "Här är resultat från TF-IDF (Med AI-analys):"
        # 1. Hämta grund-resultat
        raw_results = tfidf_model.search(message)
        # 2. Skicka dem till explainer för att få snygga texter
        recommendations = explainer_model.enrich_results(message, raw_results)
        
    elif selected_model == "nomic":
        intro = "Här är resultat från Nomic (Med AI-analys):"
        raw_results = nomic_model.search(message)
        recommendations = explainer_model.enrich_results(message, raw_results)
        
    elif selected_model == "hybrid":
        intro = "Här är resultat från Hybrid-modellen (Med AI-analys):"
        raw_results = hybrid_model.search(message)
        recommendations = explainer_model.enrich_results(message, raw_results)
        
    elif selected_model == "gemini":
        intro = "Här är vad Gemini tycker:"
        # Gemini-modellen sköter sitt eget snack, så vi kör den som vanligt
        recommendations = gemini_model.search(message)

    else:
        intro = "Okänd modell."
        recommendations = []

    return jsonify({
        "type": "json_recommendation", 
        "intro": intro,
        "data": recommendations
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)

