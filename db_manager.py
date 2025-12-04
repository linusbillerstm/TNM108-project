import sqlite3
import hashlib
from datetime import datetime

# Namnet på din databasfil (skapas automatiskt om den inte finns)
DB_NAME = "tv_chatbot.db"

def init_db():
    """Skapar tabellerna om de inte redan finns."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Tabell för användare
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Tabell för historik
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            user_query TEXT,
            bot_response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Databas initierad!")

def hash_password(password):
    """Krypterar lösenordet (SHA-256) så vi inte sparar det i klartext."""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):
    """Skapar en ny användare. Returnerar True om det gick bra, annars False."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    hashed_pw = hash_password(password)
    
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Detta händer om användarnamnet redan finns (UNIQUE constraint)
        return False
    finally:
        conn.close()

def login_user(username, password):
    """Kollar om användarnamn och lösenord stämmer. Returnerar user_id eller None."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    hashed_pw = hash_password(password)
    
    c.execute("SELECT id FROM users WHERE username = ? AND password = ?", (username, hashed_pw))
    user = c.fetchone()
    conn.close()
    
    if user:
        return user[0] # Returnerar användarens ID
    return None

def save_history(user_id, query, response):
    """Sparar vad användaren skrev och vad boten svarade."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO history (user_id, user_query, bot_response) VALUES (?, ?, ?)", 
              (user_id, query, response))
    conn.commit()
    conn.close()

def get_user_history(user_id, limit=5):
    """Hämtar de senaste konversationerna för att ge boten kontext."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Hämtar de senaste raderna
    c.execute("""
        SELECT user_query 
        FROM history 
        WHERE user_id = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
    """, (user_id, limit))
    
    rows = c.fetchall()
    conn.close()
    
    # Returnera som en enda lång textsträng (bra för TF-IDF)
    # Exempel: "jag gillar action jag gillar komedi"
    history_text = " ".join([row[0] for row in rows])
    return history_text

# Körs bara om du kör denna fil direkt, bra för att testa att det funkar
if __name__ == "__main__":
    init_db()
    # Testa att skapa en användare
    if create_user("testare", "hemligt123"):
        print("Användare skapad!")
    else:
        print("Användaren finns redan.")
        
    # Testa inloggning
    uid = login_user("testare", "hemligt123")
    if uid:
        print(f"Inloggad med ID: {uid}")
        save_history(uid, "Jag gillar skräck", "Prova The Walking Dead")
        print("Historik:", get_user_history(uid))
    else:
        print("Fel lösenord.")