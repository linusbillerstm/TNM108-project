import pandas as pd
import os
import time
import random
from flask import Flask, render_template, request, jsonify

# importera modeller
from ai_models import tfidf_model, nomic_model, gemini_model, hybrid_model, explainer_model

# så att flask hittar CSS/JS 
app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')

# initierar av modeller
def start_app():
    print("Laddar dataset och AI-modeller...")
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(base_dir, 'sorted_shows.csv')
        df = pd.read_csv(csv_path)     
        
        # tar bort NaNs
        df['combined_text'] = df['combined_text'].fillna('') 
        
        # skicka data till varje modell
        tfidf_model.init(df)
        nomic_model.init(df)
        gemini_model.init(df)
        hybrid_model.init(df)
        
        explainer_model.init()

        print("modeller laddade")
    except Exception as e:
        print(f"fel vid start av AI-modeller: {e}")
        import traceback
        traceback.print_exc()

#initiering direkt
with app.app_context():
    start_app()

# routes 

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
        intro = "Här är resultat från TF-IDF modellen:"
        raw_results = tfidf_model.search(message)
        recommendations = explainer_model.enrich_results(message, raw_results)
        
    elif selected_model == "nomic":
        intro = "Här är resultat från Nomic modellen:"
        raw_results = nomic_model.search(message)
        recommendations = explainer_model.enrich_results(message, raw_results)
        
    elif selected_model == "hybrid":
        intro = "Här är resultat från Hybrid modellen:"
        raw_results = hybrid_model.search(message)
        recommendations = explainer_model.enrich_results(message, raw_results)
        
    elif selected_model == "gemini":
        intro = "Här är resultatetet från Gemini modellen:"
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

