import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os

# globala variabler
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
        print(f"kunde inte ladda nomic: {e}")

def search(query, top_k=3):
    if model is None or embeddings is None: return []

    search_query = f"search_query: {query}"
    
    # skapa embedding för input
    query_embedding = model.encode([search_query])
    
    # jämför 
    similarities = cosine_similarity(query_embedding, embeddings).flatten()
    
    # hämta topp3
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