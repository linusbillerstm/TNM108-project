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
    
    try:
        # ladda data
        model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True)
        
        # backa en mapp där embeddings.npy finns
        current_folder = os.path.dirname(os.path.abspath(__file__))
        root_folder = os.path.dirname(current_folder)
        file_path = os.path.join(root_folder, "embeddings.npy")
        embeddings = np.load(file_path)
        
    except Exception as e:
        print(f"   [NOMIC FEL] Kunde inte ladda: {e}")

def search(query, top_k=3):
    if model is None or embeddings is None: return []

    # lägg till prefixet som i din fil
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
            "reason": f"Semantisk matchning: {int(score*100)}%",
            "rating": row['imdb_rating'],
            "score": int(score * 100)
        })
        
    return results