import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer  # Ersätter ollama
from sklearn.metrics.pairwise import cosine_similarity       # Kvarstår från PDF:en [cite: 245]

# Ladda data (samma som förut)
df = pd.read_csv('sorted_shows.csv')

# Förbered texten
df['combined_text'] = (
    "Title: " + df['title'] + 
    ". Genre: " + df['genre'] + 
    ". Storyline: " + df['storyline']
)

# --- TF-IDF SETUP (Istället för Ollama) ---
# 1. Skapa "ordboken" och vektoriseraren.
# PDF:en nämner TfidfVectorizer som standardmetod för detta[cite: 235].
# 'stop_words' tar bort vanliga ord (som 'the', 'is') precis som PDF:en föreslår[cite: 7].
vectorizer = TfidfVectorizer(stop_words='english') 

# 2. Lär upp modellen på alla dina filmer/serier och skapa matrisen.
# Detta motsvarar att skapa matrisen M i PDF:en.
tfidf_matrix = vectorizer.fit_transform(df['combined_text'])

def recommend_series(user_prompt, top_k=3):
    # A. Gör om din fråga till siffror
    # VIKTIGT FRÅN PDF: Vi använder .transform() här, INTE .fit_transform().
    # Vi måste använda samma "ordbok" som vi skapade ovan för att matcha rätt.
    prompt_vector = vectorizer.transform([user_prompt])

    # B. Räkna ut likhet
    # Vi mäter vinkeln mellan din sökning och alla serier i databasen[cite: 247].
    similarities = cosine_similarity(prompt_vector, tfidf_matrix)

    # C. Sortera fram de bästa
    # similarities returnerar en lista av listor, vi tar första raden [0].
    top_indices = similarities[0].argsort()[-top_k:][::-1]

    results = []
    for idx in top_indices:
        score = similarities[0][idx]
        series_data = df.iloc[idx]
        results.append((series_data, score))
    
    return results

# --- HUVUDPROGRAM ---
# (Denna del är identisk med din mall för att behålla stilen)
while True:
    print("\n" + "-"*30)
    user_input = input("Vad vill du se? (skriv 'q' för att avsluta): \n> ")
    
    if user_input.lower() == 'q':
        break
    
    recommendations = recommend_series(user_input)
    
    print(f"\nJag rekommenderar:\n")
    
    for i, (series, score) in enumerate(recommendations, 1):
        # Notera: TF-IDF scores är ofta lägre än AI-embeddings, men rangordningen funkar likadant.
        print(f"{i}. {series['title']} ({int(score * 100)}% match)")
        print(f"   Genre: {series['genre']}")
        print(f"   Handling: {series['storyline'][:100]}...") 
        print("")
