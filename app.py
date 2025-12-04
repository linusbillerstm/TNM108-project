import ollama
import db_manager as db
from recommender import MovieRecommender

# Initiera systemet
db.init_db()
rec_engine = MovieRecommender()
MODEL_NAME = "qwen2.5:3b" 

def generate_ai_response(user_input, recommendations):
    """Skapar prompten till Ollama och hämtar svaret."""
    
    # Gör om listan av serier till en snygg textsträng för AI:n
    rec_text = ""
    for r in recommendations:
        rec_text += f"- {r['Title']} ({r['Rating']}/10). Genre: {r['Genres']}. Handling: {r['About']}\n"

    # System-prompten styr hur AI:n beter sig
    prompt = f"""
    Du är en hjälpsam expert på TV-serier.
    Användaren vill ha tips baserat på: "{user_input}"
    
    Här är de serier som vår databas hittade som matchar bäst:
    {rec_text}
    
    Uppgift:
    1. Rekommendera 2-3 av dessa serier till användaren på svenska.
    2. Förklara kort varför de passar baserat på användarens sökning.
    3. Var trevlig och personlig.
    """

    response = ollama.chat(model=MODEL_NAME, messages=[
        {'role': 'user', 'content': prompt},
    ])
    
    return response['message']['content']

def main():
    print("\n--- VÄLKOMMEN TILL TV-SERIE BOTEN ---")
    
    # --- Enkel Inloggning ---
    while True:
        choice = input("1. Logga in\n2. Skapa konto\nVälj: ")
        if choice == "2":
            u = input("Välj användarnamn: ")
            p = input("Välj lösenord: ")
            if db.create_user(u, p):
                print("Konto skapat! Logga in nu.")
            else:
                print("Namnet upptaget.")
        elif choice == "1":
            u = input("Användarnamn: ")
            p = input("Lösenord: ")
            user_id = db.login_user(u, p)
            if user_id:
                print(f"Välkommen tillbaka, {u}!")
                break
            else:
                print("Fel inloggning.")
    
    # --- Chat Loop ---
    print("\nSkriv vad du är sugen på att se (eller 'sluta' för att avsluta).")
    
    while True:
        user_input = input("\nDu: ")
        if user_input.lower() in ['sluta', 'exit', 'quit']:
            break
        
        # 1. Hämta historik för kontext
        history = db.get_user_history(user_id)
        
        # 2. Hitta serier med TF-IDF (Hjärnan)
        recommendations = rec_engine.search(user_input, history)
        
        # 3. Låt Ollama formulera svaret
        print("Tänker...")
        bot_response = generate_ai_response(user_input, recommendations)
        
        # 4. Visa svaret
        print(f"\nBot: {bot_response}")
        
        # 5. Spara konversationen i databasen
        db.save_history(user_id, user_input, bot_response)

if __name__ == "__main__":
    main()