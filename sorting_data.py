import pandas as pd

# 1. Läs in den smutsiga filen
df = pd.read_csv("shows.csv")

# --- STÄDFUNKTIONEN ---
def clean_feature(text, limit=None):
    # Om det är tomt, returnera tom sträng
    if pd.isna(text) or text == "":
        return ""
    
    # 1. Ta bort alla "dator-tecken" (klamrar, fnuttar)
    # Exempel: "['Drama', 'Crime']"  blir  "Drama, Crime"
    clean_text = str(text).replace('[', '').replace(']', '').replace("'", "").replace('"', '')
    
    # 2. Dela upp vid kommatecken för att kunna räkna dem
    items = [item.strip() for item in clean_text.split(',')]
    
    # 3. Om vi har en gräns (t.ex max 5 skådisar), klipp listan
    if limit and len(items) > limit:
        items = items[:limit]
            
    # 4. Sätt ihop igen med snygga kommatecken
    return ', '.join(items)

print("Städar datan...")

# Applicera städningen
# För genrer tar vi max 3 (viktigast först)
df['genre'] = df['genre'].apply(lambda x: clean_feature(x, limit=3))

# För skådespelare tar vi max 5 (huvudrollerna)
df['cast_name'] = df['cast_name'].apply(lambda x: clean_feature(x, limit=5))

# För storyline tar vi bort onödiga mellanslag i början/slutet
df['storyline'] = df['storyline'].astype(str).str.strip()

# Välj de kolumner du vill spara
features = [
    'rank', 
    'title', 
    'year', 
    'imdb_votes', 
    'imdb_rating', 
    'duration', 
    'genre', 
    'cast_name', 
    'director_name', 
    'storyline'
]

# Skapa den sorterade tabellen
df_sorted = df[features]

# Spara till ny fil (utan index-siffrorna till vänster)
df_sorted.to_csv('sorted_shows.csv', index=False)

print("\n--- KLART! ---")
print("Exempel på hur datan ser ut nu:")
print(f"Genre: {df_sorted['genre'].iloc[0]}")
print(f"Cast:  {df_sorted['cast_name'].iloc[0]}")
