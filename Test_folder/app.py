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

# import sqlite3
# from flask import Flask, render_template, request, jsonify, session
# from werkzeug.security import generate_password_hash, check_password_hash
# import time
# import random

# # Vi säger åt Flask att leta efter HTML och CSS i samma mapp (.)
# app = Flask(__name__, template_folder='.', static_folder='.', static_url_path='')
# app.secret_key = "hemlig_nyckel_123" # Krävs för att komma ihåg inloggning

# # --- 1. DATABAS (Skapas automatiskt) ---
# def init_db():
#     conn = sqlite3.connect('series_data.db')
#     c = conn.cursor()
#     # Tabell för användare
#     c.execute('''CREATE TABLE IF NOT EXISTS users 
#                  (id INTEGER PRIMARY KEY AUTOINCREMENT, 
#                   username TEXT UNIQUE NOT NULL, 
#                   password TEXT NOT NULL)''')
    
#     # Tabell för gillade serier (Kopplad till användarens ID)
#     c.execute('''CREATE TABLE IF NOT EXISTS liked_series 
#                  (id INTEGER PRIMARY KEY AUTOINCREMENT, 
#                   user_id INTEGER, 
#                   title TEXT, 
#                   FOREIGN KEY(user_id) REFERENCES users(id),
#                   UNIQUE(user_id, title))''')
#     conn.commit()
#     conn.close()

# # Kör databas-funktionen när programmet startar
# init_db()

# # Hjälpfunktion för att koppla upp mot databasen
# def get_db():
#     conn = sqlite3.connect('series_data.db')
#     conn.row_factory = sqlite3.Row # Gör att vi kan hämta data med namn
#     return conn

# # --- 2. ROUTES (Vägval) ---

# @app.route('/')
# def index():
#     return render_template('index.html')

# # -- INLOGGNING & REGISTRERING --

# @app.route('/register', methods=['POST'])
# def register():
#     data = request.json
#     username = data.get('username')
#     password = data.get('password')
    
#     # Kryptera lösenordet innan vi sparar det
#     hashed_pw = generate_password_hash(password)
    
#     try:
#         conn = get_db()
#         conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
#         conn.commit()
#         conn.close()
#         return jsonify({"status": "success", "message": "Konto skapat! Logga in."})
#     except sqlite3.IntegrityError:
#         return jsonify({"status": "error", "message": "Användarnamnet upptaget."})

# @app.route('/login', methods=['POST'])
# def login():
#     data = request.json
#     username = data.get('username')
#     password = data.get('password')
    
#     conn = get_db()
#     user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
#     conn.close()
    
#     # Kolla om användaren finns och om lösenordet stämmer
#     if user and check_password_hash(user['password'], password):
#         session['user_id'] = user['id'] # Spara inloggning i sessionen
#         session['username'] = user['username']
#         return jsonify({"status": "success", "username": user['username']})
#     else:
#         return jsonify({"status": "error", "message": "Fel användarnamn eller lösenord"})

# @app.route('/logout', methods=['POST'])
# def logout():
#     session.clear() # Töm sessionen
#     return jsonify({"status": "success"})

# @app.route('/check_session', methods=['GET'])
# def check_session():
#     # Kollar om någon är inloggad när sidan laddas om
#     if 'user_id' in session:
#         return jsonify({"logged_in": True, "username": session['username']})
#     return jsonify({"logged_in": False})

# # -- GILLA SERIER --

# @app.route('/like', methods=['POST'])
# def like_series():
#     # Säkerhetskoll: Är man inloggad?
#     if 'user_id' not in session:
#         return jsonify({"status": "error", "message": "Du måste logga in för att spara!"}), 401

#     data = request.json
#     title = data.get('title')
#     user_id = session['user_id']
    
#     conn = get_db()
#     try:
#         conn.execute("INSERT INTO liked_series (user_id, title) VALUES (?, ?)", (user_id, title))
#         conn.commit()
#         msg = "Sparad!"
#     except sqlite3.IntegrityError:
#         msg = "Redan sparad!" # Om man redan gillat den
#     finally:
#         conn.close()
    
#     return jsonify({"status": "success", "message": msg})

# # -- LÅTSAS-CHAT (För test) --
# @app.route('/chat', methods=['POST'])
# def chat():
#     # 1. Hämta vad användaren skrev
#     user_message = request.json.get('message', '')
    
#     # Simulera att AI:n "tänker" i 1-2 sekunder
#     time.sleep(random.uniform(0.5, 1.5))
    
#     # 2. Skapa lite olika svar beroende på input (bara för show just nu)
#     # Detta gör att det känns mer som en riktig AI tills vi kopplar in Gemini
    
#     recommendations = []
    
#     if "rolig" in user_message.lower() or "komedi" in user_message.lower():
#         recommendations = [
#             {"title": "Friends", "year": "1994", "reason": "En klassisk sitcom som alltid levererar skratt."},
#             {"title": "The Office", "year": "2005", "reason": "Pinsam humor och mockumentär-stil när den är som bäst."},
#             {"title": "Seinfeld", "year": "1989", "reason": "Serien om ingenting som ändå är om allt."}
#         ]
#         intro_text = "Här är några komedier som garanterat får dig att skratta:"
        
#     elif "spännande" in user_message.lower() or "action" in user_message.lower():
#         recommendations = [
#             {"title": "Breaking Bad", "year": "2008", "reason": "Otroligt intensiv utveckling från lärare till drogbaron."},
#             {"title": "Game of Thrones", "year": "2011", "reason": "Eposet som definierade 2010-talets TV-drama."},
#             {"title": "Sherlock", "year": "2010", "reason": "Snabbt, smart och väldigt spännande."}
#         ]
#         intro_text = "Om du vill ha spänning är dessa svårslagna:"
        
#     else:
#         # Standard-svar om vi inte förstår
#         recommendations = [
#             {"title": "Planet Earth II", "year": "2016", "reason": "Världens högst rankade serie av en anledning."},
#             {"title": "Band of Brothers", "year": "2001", "reason": "Ett mästerverk om andra världskriget."},
#             {"title": "Chernobyl", "year": "2019", "reason": "Mörk, verklighetsbaserad och omöjlig att sluta titta på."}
#         ]
#         intro_text = "Här är tre av de absolut bästa serierna någonsin:"

#     # Returnera både text och data
#     return jsonify({
#         "type": "json_recommendation", 
#         "intro": intro_text,     # Vi skickar med en intro-text också
#         "data": recommendations
#     })

# if __name__ == '__main__':
#     app.run(debug=True, port=5000)