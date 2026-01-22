import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# Globala variabler
model = None
embeddings = None
count_vectorizer = None
tfidf_transformer = None
tfidf_matrix = None
df_ref = None

def normalize(scores):
    """Hjälpfunktion för att skala värden till 0-1"""
    if np.max(scores) == np.min(scores):
        return scores
    return (scores - np.min(scores)) / (np.max(scores) - np.min(scores))

def init(df):
    global model, embeddings, count_vectorizer, tfidf_transformer, tfidf_matrix, df_ref
    df_ref = df
    
    print("   [HYBRID] Initierar modell...")
    
    try:
        # 1. Ladda Nomic (Embeddings)
        model = SentenceTransformer("nomic-ai/nomic-embed-text-v1.5", trust_remote_code=True)
        embeddings = np.load("embeddings.npy")
        
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
        # Filtrera bort dåliga matchningar (t.ex. under 35% säkerhet)
        if score < 0.35:
            continue
            
        row = df_ref.iloc[idx]
        results.append({
            "title": row['title'],
            "year": int(row['year']),
            "reason": f"Hybrid Match ({int(score*100)}% säkerhet) - Kombinerar ord och mening."
        })
        
    if not results:
        return [{"title": "Ingen träff", "year": 0, "reason": "Ingen serie matchade tillräckligt bra (över 35%)."}]

    return results

# import pandas as pd
# import numpy as np
# import ollama
# from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
# from sklearn.metrics.pairwise import cosine_similarity

# #laddar data
# df = pd.read_csv("sorted_shows.csv", engine='python', on_bad_lines='skip').fillna('')
# embeddings_matrix = np.load('embeddings.npy')
    
# #tar bort fyllnadstext för att inte påverka sökningen
# common_words = list(CountVectorizer(stop_words='english').get_stop_words())
# common_words.extend(['serie', 'series', 'show', 'tv', 'watch', 'want', 'give', 'recommend'])

# #skapar en matris som räknar förekomsten av ord
# count_vectorizer = CountVectorizer(stop_words=common_words, ngram_range=(1, 2))
# count_matrix = count_vectorizer.fit_transform(df['combined_text'])
    
# #viktar ord baserat hur unika de är
# tfidf_transformer = TfidfTransformer(norm='l2') # L2-normering
# tfidf_matrix = tfidf_transformer.fit_transform(count_matrix)
    
# #skala 0-1
# def normalize(scores):
#     if np.max(scores) == np.min(scores): return scores
#     return (scores - np.min(scores)) / (np.max(scores) - np.min(scores))

# def search(query):
    
#     #TF-IDF

#     #omvandlar söktext till frekvens, gör om till vektor av antal
#     query_counts = count_vectorizer.transform([query])
    
#     #viktar frekvenser för tf-idf, hur viktiga är varje ord
#     query_tfidf_vec = tfidf_transformer.transform(query_counts)
    
#     #jämför sökvektor med alla serier i datan
#     tfidf_scores = cosine_similarity(query_tfidf_vec, tfidf_matrix).flatten()
    
#     #Embeddings

#     #skickar söktext till ollama, gör om till vektor
#     response = ollama.embeddings(model="nomic-embed-text", prompt=query)

#     #embeddar sökorden
#     query_matrix = np.array(response['embedding']).reshape(1, -1)

#     #jämför sökordens betydelse med datans betydelse
#     embed_scores = cosine_similarity(query_matrix, embeddings_matrix).flatten()
    
#     #viktar TF-IDF och Embeddings 50/50
#     final_scores = (0.5 * normalize(tfidf_scores)) + ((1 - 0.5) * normalize(embed_scores))
#     #soretrar poäng, spara topp 3
#     top_indices = final_scores.argsort()[-3:][::-1]
    
#     #loopar igenom de tre bästa resultaten
#     context = ""
#     print("\n--- Matches ---")
#     for idx in top_indices:

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