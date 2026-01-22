import pandas as pd
import sqlite3
import os
from flask import Flask, render_template, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash

# --- IMPORTERA DINA NYA MODELLER ---
from ai_models import tfidf_model, nomic_model, gemini_model

app = Flask(__name__, template_folder='.', static_folder='static') # Notera static mappen
app.secret_key = "super_hemlig_nyckel"

# --- INITIERING (Körs en gång vid start) ---
def start_app():
    print("⏳ Laddar dataset och AI-modeller...")
    try:
        # Läs in CSV-filen en gång för alla
        df = pd.read_csv('sorted_shows.csv')
        df['combined_text'] = df['combined_text'].fillna('') # Fixa tomma rader
        
        # Skicka datan till varje modell så de kan förbereda sig
        tfidf_model.init(df)
        nomic_model.init(df)
        gemini_model.init(df)
        
        print("✅ Allt laddat och klart!")
    except Exception as e:
        print(f"❌ Kritiskt fel vid start: {e}")

# Kör initieringen
with app.app_context():
    start_app()

# --- DATABAS (Behåll din gamla kod här) ---
def get_db():
    conn = sqlite3.connect('series_data.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS liked_series 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, title TEXT, 
                  FOREIGN KEY(user_id) REFERENCES users(id), UNIQUE(user_id, title))''')
    conn.commit()
    conn.close()

init_db()

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

# (Behåll dina rutor för login/register/logout/like här - de ändras inte)
# ... Klistra in dem från din förra app.py ...
# Jag kortar ner koden här för överskådlighet, men du ska ha kvar dem!

@app.route('/login', methods=['POST'])
def login():
    # ... din login kod ...
    return jsonify({"status": "success", "username": "TestUser"}) # Placeholder

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"status": "success"})

@app.route('/check_session', methods=['GET'])
def check_session():
    if 'user_id' in session:
        return jsonify({"logged_in": True, "username": session['username']})
    return jsonify({"logged_in": False})


# --- CHAT ROUTE (Här väljer vi fil!) ---
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message', '')
    selected_model = data.get('model', 'tfidf') # Standardval
    
    recommendations = []
    intro = ""

    # SWITCH-CASE FÖR MODELLERNA
    if selected_model == "tfidf":
        intro = "Här är resultat från TF-IDF (Nyckelord):"
        recommendations = tfidf_model.search(message)
        
    elif selected_model == "nomic":
        intro = "Här är resultat från Nomic (Semantisk Sökning):"
        recommendations = nomic_model.search(message)
        
    elif selected_model == "gemini":
        intro = "Här är vad Gemini tycker:"
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

# import ollama
# import db_manager as db
# from recommender import MovieRecommender

# # Initiera systemet
# db.init_db()
# rec_engine = MovieRecommender()
# MODEL_NAME = "qwen2.5:3b" 

# def generate_ai_response(user_input, recommendations):
#     """Skapar prompten till Ollama och hämtar svaret."""
    
#     # Gör om listan av serier till en snygg textsträng för AI:n
#     rec_text = ""
#     for r in recommendations:
#         rec_text += f"- {r['Title']} ({r['Rating']}/10). Genre: {r['Genres']}. Handling: {r['About']}\n"

#     # System-prompten styr hur AI:n beter sig
#     prompt = f"""
#     Du är en hjälpsam expert på TV-serier.
#     Användaren vill ha tips baserat på: "{user_input}"
    
#     Här är de serier som vår databas hittade som matchar bäst:
#     {rec_text}
    
#     Uppgift:
#     1. Rekommendera 2-3 av dessa serier till användaren på svenska.
#     2. Förklara kort varför de passar baserat på användarens sökning.
#     3. Var trevlig och personlig.
#     """

#     response = ollama.chat(model=MODEL_NAME, messages=[
#         {'role': 'user', 'content': prompt},
#     ])
    
#     return response['message']['content']

# def main():
#     print("\n--- VÄLKOMMEN TILL TV-SERIE BOTEN ---")
    
#     # --- Enkel Inloggning ---
#     while True:
#         choice = input("1. Logga in\n2. Skapa konto\nVälj: ")
#         if choice == "2":
#             u = input("Välj användarnamn: ")
#             p = input("Välj lösenord: ")
#             if db.create_user(u, p):
#                 print("Konto skapat! Logga in nu.")
#             else:
#                 print("Namnet upptaget.")
#         elif choice == "1":
#             u = input("Användarnamn: ")
#             p = input("Lösenord: ")
#             user_id = db.login_user(u, p)
#             if user_id:
#                 print(f"Välkommen tillbaka, {u}!")
#                 break
#             else:
#                 print("Fel inloggning.")
    
#     # --- Chat Loop ---
#     print("\nSkriv vad du är sugen på att se (eller 'sluta' för att avsluta).")
    
#     while True:
#         user_input = input("\nDu: ")
#         if user_input.lower() in ['sluta', 'exit', 'quit']:
#             break
        
#         # 1. Hämta historik för kontext
#         history = db.get_user_history(user_id)
        
#         # 2. Hitta serier med TF-IDF (Hjärnan)
#         recommendations = rec_engine.search(user_input, history)
        
#         # 3. Låt Ollama formulera svaret
#         print("Tänker...")
#         bot_response = generate_ai_response(user_input, recommendations)
        
#         # 4. Visa svaret
#         print(f"\nBot: {bot_response}")
        
#         # 5. Spara konversationen i databasen
#         db.save_history(user_id, user_input, bot_response)

# if __name__ == "__main__":
#     main()