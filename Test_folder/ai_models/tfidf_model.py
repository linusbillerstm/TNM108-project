import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Globala variabler
count_vectorizer = None
tfidf_transformer = None
tfidf_matrix = None
df_ref = None

def init(df):
    """Körs av app.py vid start"""
    global count_vectorizer, tfidf_transformer, tfidf_matrix, df_ref
    df_ref = df
    
    print("   [TF-IDF] Tränar vektoriserare...")
    
    #tar bort fyllnadstext för att inte påverka sökningen
    common_words = list(CountVectorizer(stop_words='english').get_stop_words())
    common_words.extend(['serie', 'series', 'show', 'tv', 'watch', 'want', 'give', 'recommend'])

    #skapar en matris som räknar förekomsten av ord
    count_vectorizer = CountVectorizer(stop_words=common_words, ngram_range=(1, 2))
    count_matrix = count_vectorizer.fit_transform(df['combined_text'])

    #viktar ord baserat hur unika de är
    tfidf_transformer = TfidfTransformer(norm='l2')
    tfidf_matrix = tfidf_transformer.fit_transform(count_matrix)


def search(query, top_k=5):
    """Samma söklogik, men returnerar en lista"""
    if count_vectorizer is None: return []

    # Omvandla sökning
    query_counts = count_vectorizer.transform([query])

    query_vec = tfidf_transformer.transform(query_counts)
    
    # Räkna ut likhet
    similarity_scores = cosine_similarity(query_vec, tfidf_matrix).flatten()
    
    # Hämta topp-index
    top_indices = np.argsort(similarity_scores)[-top_k:][::-1]
    
    results = []
    for idx in top_indices:
        score_percent = int(similarity_scores[idx] * 100)
        # Din logik för att skippa 0-matchningar
        if similarity_scores[idx] == 0:
            continue
            
        row = df_ref.iloc[idx]
        results.append({
            "title": row['title'],
            "year": str(row['year']), # Konvertera till int för snyggare JSON
            "reason": f"Matchar nyckelord i: {str(row['genre'])}",
            "score": score_percent,
            "rating": row['imdb_rating']
        })
    
    return results