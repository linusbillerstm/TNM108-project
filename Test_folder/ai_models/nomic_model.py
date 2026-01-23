import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os

# Globala variabler
model = None
embeddings = None
df_ref = None

def init(df):
    """Körs av app.py vid start"""
    global model, embeddings, df_ref
    df_ref = df
    
    print("   [NOMIC] Laddar modell och embeddings...")
    try:
        # Ladda modellen (Samma som i din fil)
        model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True)
        
        # backa en mapp där embeddings.npy finns
        current_folder = os.path.dirname(os.path.abspath(__file__))
        root_folder = os.path.dirname(current_folder)
        file_path = os.path.join(root_folder, "embeddings.npy")
        embeddings = np.load(file_path)
        
    except Exception as e:
        print(f"   [NOMIC FEL] Kunde inte ladda: {e}")

def search(query, top_k=5):
    if model is None or embeddings is None: return []

    # Lägg till prefixet som i din fil
    search_query = f"search_query: {query}"
    
    # Skapa embedding för frågan
    query_embedding = model.encode([search_query])
    
    # Jämför
    similarities = cosine_similarity(query_embedding, embeddings).flatten()
    
    # Hämta topp-index
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    
    results = []
    for idx in top_indices:
        row = df_ref.iloc[idx]
        score = similarities[idx]
        
        results.append({
            "title": row['title'],
            "year": str(row['year']),
            "reason": f"Semantisk matchning: {int(score*100)}%"
        })
        
    return results



# import pandas as pd
# import numpy as np
# import ollama
# from sklearn.metrics.pairwise import cosine_similarity

# #laddar data
# df = pd.read_csv("sorted_shows.csv", engine='python', on_bad_lines='skip').fillna('')
# embeddings_matrix = np.load('embeddings.npy')

# def search(query):
    
#     #skickar söktext till ollama, gör om till vektor
#     response = ollama.embeddings(model="nomic-embed-text", prompt=query)

#     #embeddar sökorden (gör om till 2D-matris 1x768)
#     query_matrix = np.array(response['embedding']).reshape(1, -1)

#     #jämför sökordens betydelse med datans betydelse
#     embed_scores = cosine_similarity(query_matrix, embeddings_matrix).flatten()
    
#     #Använder bara Embedding poäng direkt
#     final_scores = embed_scores
    
#     #soretrar poäng, spara topp 3
#     top_shows = final_scores.argsort()[-3:][::-1]
    
#     #loopar igenom de tre bästa resultaten
#     context = ""
#     print("\n--- Matches: ---")
#     for idx in top_shows:

#         #(> 35%)
#         if final_scores[idx] > 0.35: 
#             #hämtar data
#             row = df.iloc[idx]
#             match_score = round(final_scores[idx] * 100, 1)
#             #lägger till i context
#             print(f" • {row['title']} ({match_score}%)")
#             context += f"Show: {row['title']} ({row['year']})\nStory: {str(row['storyline'])[:300]}...\n---\n"

#     if not context:
#         print("Bot: No good matches found.")
#         return

#     #instruktioner
#     prompt = f"""
#     User search: "{query}"
    
#     Potential Matches (Data from database):
#     {context}

#     Task: Recommend ONLY the shows from the list above that actully fit the user's search.
    
#     CRITICAL RULES:
#     1. RELY ONLY ON THE PROVIDED STORY. Do NOT use outside knowledge.
#     2. If a show's story does NOT mention the search topic, DO NOT recommend it. Say "Found match by keywords, but story doesn't fit."
#     3. Do NOT invent facts.
#     """
    
#     print("\nBot: ", end="", flush=True)
#     try:
#         #livesvar
#         stream = ollama.chat(model="llama3.2:1b", messages=[{'role': 'user', 'content': prompt}], stream=True)
#         for chunk in stream:
#             print(chunk['message']['content'], end="", flush=True)
#         print("\n")
#     except Exception as e:
#         print(f"Error: {e}")

# #main-loop
# print("\nWhat TV-show are you locking for? ('q' to quit)")
# while True:
#     q = input("\nYou: ")
#     if q.lower() in ['q', 'quit']: break
#     search(q)
#     print("-" * 50)