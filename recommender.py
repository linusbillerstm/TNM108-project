import pandas as pd
import ollama
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

df = pd.read_csv('sorted_shows.csv')

df['combined_text'] = (
    "Title: " + df['title'] + 
    ". Genre: " + df['genre'] + 
    ". Storyline: " + df['storyline']
)

embeddings = []

for text in df['combined_text']:
    response = ollama.embeddings(model='nomic-embed-text', prompt=text)
    embeddings.append(response['embedding'])

embeddings_matrix = np.array(embeddings)

def recommend_series(user_prompt, top_k=3):
    # A. Gör om din fråga till siffror
    response = ollama.embeddings(model='nomic-embed-text', prompt=user_prompt)
    prompt_embedding = np.array([response['embedding']])

    # B. Räkna ut likhet
    similarities = cosine_similarity(prompt_embedding, embeddings_matrix)

    # C. Sortera fram de bästa
    top_indices = similarities[0].argsort()[-top_k:][::-1]

    results = []
    for idx in top_indices:
        score = similarities[0][idx]
        series_data = df.iloc[idx]
        results.append((series_data, score))
    
    return results

# --- HUVUDPROGRAM ---
while True:
    print("\n" + "-"*30)
    user_input = input("Vad vill du se? (skriv 'q' för att avsluta): \n> ")
    
    if user_input.lower() == 'q':
        break
    
    recommendations = recommend_series(user_input)
    
    print(f"\nJag rekommenderar:\n")
    
    for i, (series, score) in enumerate(recommendations, 1):
        print(f"{i}. {series['title']} ({int(score * 100)}% match)")
        print(f"   Genre: {series['genre']}")
        print(f"   Handling: {series['storyline'][:100]}...") 
        print("")
