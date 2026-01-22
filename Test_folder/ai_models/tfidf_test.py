import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Globala variabler
vectorizer = None
tfidf_matrix = None
df_ref = None

def init(df):
    """Körs av app.py vid start"""
    global vectorizer, tfidf_matrix, df_ref
    df_ref = df
    
    print("   [TF-IDF] Tränar vektoriserare...")
    # Din logik för att skapa combined_text om den inte finns
    if 'combined_text' not in df.columns:
        df['combined_text'] = df['title'] + " " + df['genre'] + " " + df['storyline']
    
    # Fyll tomma värden
    text_data = df['combined_text'].fillna('')
    
    # Samma inställningar som i din fil
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(text_data)

def search(query, top_k=5):
    """Samma söklogik, men returnerar en lista"""
    if vectorizer is None: return []

    # Omvandla sökning
    query_vec = vectorizer.transform([query])
    
    # Räkna ut likhet
    similarity_scores = cosine_similarity(query_vec, tfidf_matrix).flatten()
    
    # Hämta topp-index
    top_indices = np.argsort(similarity_scores)[-top_k:][::-1]
    
    results = []
    for idx in top_indices:
        # Din logik för att skippa 0-matchningar
        if similarity_scores[idx] == 0:
            continue
            
        row = df_ref.iloc[idx]
        results.append({
            "title": row['title'],
            "year": int(row['year']), # Konvertera till int för snyggare JSON
            "reason": f"Matchar nyckelord i: {str(row['genre'])}"
        })
    
    return results

# #laddar data
# df = pd.read_csv("sorted_shows.csv", engine='python', on_bad_lines='skip').fillna('')

# #tar bort fyllnadstext för att inte påverka sökningen
# common_words = list(CountVectorizer(stop_words='english').get_stop_words())
# common_words.extend(['serie', 'series', 'show', 'tv', 'watch', 'want', 'give', 'recommend'])

# #skapar en matris som räknar förekomsten av ord
# count_vectorizer = CountVectorizer(stop_words=common_words, ngram_range=(1, 2))
# count_matrix = count_vectorizer.fit_transform(df['combined_text'])
    
# #viktar ord baserat hur unika de är
# tfidf_transformer = TfidfTransformer(norm='l2') # L2-normering
# tfidf_matrix = tfidf_transformer.fit_transform(count_matrix)

# def search(query):
    
#     #TF-IDF

#     #omvandlar söktext till frekvens, gör om till vektor av antal
#     query_counts = count_vectorizer.transform([query])
    
#     #viktar frekvenser för tf-idf, hur viktiga är varje ord
#     query_tfidf_vec = tfidf_transformer.transform(query_counts)
    
#     #jämför sökvektor med alla serier i datan
#     tfidf_scores = cosine_similarity(query_tfidf_vec, tfidf_matrix).flatten()

#     #Använder bara TF-IDF poäng direkt
#     final_scores = tfidf_scores
    
#     #soretrar poäng, spara topp 3
#     top_shows = final_scores.argsort()[-3:][::-1]
    
#     #loopar igenom de tre bästa resultaten
#     context = ""
#     print("\n--- Matches: ---")
#     for idx in top_shows:

#         #(> 0% för TF-IDF eftersom den ofta är 0 om ord inte matchar exakt)
#         if final_scores[idx] > 0: 
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