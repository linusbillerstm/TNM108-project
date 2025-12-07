import pandas as pd
import numpy as np
import ollama
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

# --- CONFIGURATION ---
EMBED_MODEL = "nomic-embed-text"
LLM_MODEL = "qwen3:8b" # Optional: if you want the AI to talk at the end

# 1. LOAD DATA
print("1. Loading Data...")
try:
    df = pd.read_csv('sorted_shows.csv')
except FileNotFoundError:
    print("Error: 'sorted_shows.csv' not found.")
    exit()

# 2. CREATE "RICH CONTEXT" (The Database Side)
# We combine Title + Genre + Storyline into one block of text
print("2. Preparing Data (Combining Title + Genre + Plot)...")
df['combined_text'] = (
    "Title: " + df['title'].astype(str) + ". " +
    "Genre: " + df['genre'].astype(str) + ". " +
    "Plot: " + df['storyline'].fillna('')
)

# 3. DEFINE EMBEDDING FUNCTION
def get_embedding(text, prefix="search_document: "):
    """
    Calls Ollama to get the vector.
    Prefix is important for nomic-embed-text!
    """
    try:
        response = ollama.embeddings(model=EMBED_MODEL, prompt=prefix + text)
        return response['embedding']
    except Exception as e:
        print(f"Error: {e}")
        return np.zeros(768).tolist()

# 4. INDEX THE DATABASE (Run once on startup)
print("3. Creating Embeddings for all shows... (This takes a moment)")
embeddings_matrix = []

# Loop through every show and turn the 'combined_text' into numbers
for text in tqdm(df['combined_text']):
    embeddings_matrix.append(get_embedding(text))

embeddings_matrix = np.array(embeddings_matrix)
print("\nSystem Ready! Database Indexed.\n")


# --- THE INTERACTIVE PART ---

def search_shows(user_input):
    print(f"\n> Converting your prompt '{user_input}' into numbers...")
    
    # ---------------------------------------------------------
    # THIS IS THE PART YOU ASKED ABOUT
    # We must embed the User's Input using the SAME model
    # ---------------------------------------------------------
    user_vector = get_embedding(user_input, prefix="search_query: ")
    
    # Reshape for the math function
    user_vector = np.array(user_vector).reshape(1, -1)
    
    # Compare User Vector vs. All Movie Vectors (Cosine Similarity)
    similarities = cosine_similarity(user_vector, embeddings_matrix)
    
    # Sort to find the highest scores (Top 3)
    top_indices = np.argsort(similarities[0])[-3:][::-1]
    
    results = []
    for idx in top_indices:
        results.append({
            "Title": df.iloc[idx]['title'],
            "Genre": df.iloc[idx]['genre'],
            "Score": similarities[0][idx], # How close was the match?
            "Plot": df.iloc[idx]['storyline']
        })
    return results

# --- MAIN LOOP ---
if __name__ == "__main__":
    while True:
        # This is the prompt where the user writes the description
        user_desc = input("\nWrite a description of what you want to watch (or 'q' to quit):\n>>> ")
        
        if user_desc.lower() in ['q', 'quit']:
            break
        
        # Run the search
        matches = search_shows(user_desc)
        
        print("\n--- Best Matches Based on Your Description ---")
        for i, m in enumerate(matches):
            print(f"{i+1}. {m['Title']} (Score: {m['Score']:.4f})")
            print(f"   Genre: {m['Genre']}")
            print(f"   Plot: {m['Plot'][:150]}...") # Show first 150 chars of plot
            print("-" * 30)