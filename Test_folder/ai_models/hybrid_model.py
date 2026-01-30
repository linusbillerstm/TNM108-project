import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import os
# Globala variabler
model = None
embeddings = None
count_vectorizer = None
tfidf_transformer = None
tfidf_matrix = None
df_ref = None

def normalize(scores):
    """Hjälpfunktion för att skala värden till 0-1"""
    if np.max(scores) == np.min(scores):return scores
    return (scores - np.min(scores)) / (np.max(scores) - np.min(scores))

def init(df):
    global model, embeddings, count_vectorizer, tfidf_transformer, tfidf_matrix, df_ref
    df_ref = df
    
    print("   [HYBRID] Initierar modell...")
    
    try:
        # 1. Ladda Nomic (Embeddings)
        model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True)
        # backa en mapp där embeddings.npy finns
        current_folder = os.path.dirname(os.path.abspath(__file__))
        root_folder = os.path.dirname(current_folder)
        file_path = os.path.join(root_folder, "embeddings.npy")
        embeddings = np.load(file_path)
        
        # 2. Ladda TF-IDF (Samma logik som i din hybrid_test.py)
        # Egna stoppord för att filtrera bort brus
        custom_stop_words = list(CountVectorizer(stop_words='english').get_stop_words())
        custom_stop_words.extend(['serie', 'series', 'show', 'tv', 'watch', 'want', 'give', 'recommend'])
        
        # Skapa matriser
        count_vectorizer = CountVectorizer(stop_words=custom_stop_words, ngram_range=(1, 2))
        
        # Kontrollera att combined_text finns
        if 'combined_text' not in df.columns:
            df['combined_text'] = df['title'].fillna('') + " " + df['genre'].fillna('') + " " + df['storyline'].fillna('')
            
        count_matrix = count_vectorizer.fit_transform(df['combined_text'].fillna(''))
        
        tfidf_transformer = TfidfTransformer(norm='l2')
        tfidf_matrix = tfidf_transformer.fit_transform(count_matrix)
        
    except Exception as e:
        print(f"   [HYBRID FEL] {e}")

def search(query, top_k=3):
    if model is None or tfidf_matrix is None: return []

    # --- 1. TF-IDF Poäng ---
    query_counts = count_vectorizer.transform([query])
    query_tfidf = tfidf_transformer.transform(query_counts)
    tfidf_scores = cosine_similarity(query_tfidf, tfidf_matrix).flatten()

    # --- 2. Embedding Poäng ---
    # Notera: Nomic behöver "search_query: " prefixet
    query_embed = model.encode([f"search_query: {query}"])
    embed_scores = cosine_similarity(query_embed, embeddings).flatten()

    # --- 3. Hybrid Kombination (50/50) ---
    # Vi normaliserar båda så de får samma "vikt" (0 till 1)
    final_scores = (0.5 * normalize(tfidf_scores)) + (0.5 * normalize(embed_scores))
    
    # Sortera och ta fram topp-resultat
    top_indices = np.argsort(final_scores)[-top_k:][::-1]
    
    results = []
    for idx in top_indices:
        score = final_scores[idx]
        
        if score < 0.35:
            continue
            
        row = df_ref.iloc[idx]
        results.append({
            "title": row['title'],
            "year": str(row['year']),
            "rating": row['imdb_rating'],
            "reason": f"Hybrid Match ({int(score*100)}% säkerhet) - Kombinerar ord och mening.",
            "score": int(score * 100)
        })
    #sorterar baserat på IMDB ranking
    #results.sort(key=lambda x: x['rating'], reverse=True)
    
        
    if not results:
        return [{"title": "Ingen träff", "year": 0, "reason": "Ingen serie matchade tillräckligt bra (över 35%)."}]

    return results