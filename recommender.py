import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class MovieRecommender:
    def __init__(self, data_file="processed_tvshows.csv"):
        # Ladda in den förbehandlade datan
        try:
            self.df = pd.read_csv(data_file)
            # Se till att inga NaN värden kraschar programmet
            self.df['combined_features'] = self.df['combined_features'].fillna('')
        except FileNotFoundError:
            print(f"FEL: Hittade inte {data_file}. Har du kört compileKeywords.py?")
            exit()

        # Skapa TF-IDF matrisen direkt när programmet startar
        print("Tränar TF-IDF modellen...")
        self.tfidf = TfidfVectorizer(stop_words='english')
        self.tfidf_matrix = self.tfidf.fit_transform(self.df['combined_features'])
        print("Klar!")

    def search(self, user_query, history="", top_n=5):
        # Ge den nuvarande prompten (user_query) mycket mer vikt än historiken
        # Genom att upprepa user_query 3 gånger blir den viktigare för TF-IDF
        full_query = f"{history} {user_query} {user_query} {user_query}"
        
        query_vec = self.tfidf.transform([full_query])
        similarity = cosine_similarity(query_vec, self.tfidf_matrix)
        
        top_indices = similarity[0].argsort()[-top_n:][::-1]
        
        results = []
        for idx in top_indices:
            row = self.df.iloc[idx]
            # Debug-print för att se varför en serie valdes (ta bort sen)
            # print(f"Matchade: {row['Title']} - Score: {similarity[0][idx]}")
            
            results.append({
                'Title': row['Title'],
                'About': row['About'],
                'Rating': row['Rating'],
                'Genres': row['Genres'],
                'Actors': row['Actors'] # Lägg till Actors här så Ollama ser dem!
            })
            
        return results