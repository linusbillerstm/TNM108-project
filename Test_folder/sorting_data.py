import pandas as pd
import numpy as np
import ollama

# ladda data, ta bort trasiga rader
df = pd.read_csv("cleaned_dataset.csv", engine='python', on_bad_lines='skip')
# nya tydliagre namn
df = df.rename(columns={ 'Title': 'title', 'About': 'storyline', 'Genres': 'genre',
                         'Actors': 'cast_name', 'Rating': 'imdb_rating', 
                         'Years': 'year'})

def clean_text(text):

    if pd.isna(text): # "" istället för NaN
        return ""
    return str(text).strip().replace("\n", " ") # tar bort onödiga mellanrum och radbrytning

for col in ['title', 'storyline', 'genre', 'cast_name']:
    df[col] = df[col].apply(clean_text)

df['imdb_rating'] = df['imdb_rating'].fillna(0) # inget betyg blir 0

df['combined_text'] = ( 
    "Title: " + df['title'] + " " +
    "Year: " + df['year'].astype(str) + " " +
    "Genre: " + df['genre'] + " " +
    "Cast: " + df['cast_name'] + ". " +
    "Story: " + df['storyline'] + "."
)

df['rank'] = range(1, len(df) + 1) # bra då de finns the Office US och UK

cols_to_keep = ['rank', 'title', 'year', 'imdb_rating', 'genre', 'cast_name', 'storyline', 'combined_text']
cols_to_keep = [c for c in cols_to_keep if c in df.columns]
df_sorted = df[cols_to_keep]
df_sorted.to_csv("sorted_shows.csv", index=False)

# embeddings
embeddings = []
iterable = df_sorted['combined_text']

for text in iterable:
    response = ollama.embeddings(model="nomic-embed-text", prompt=text)
    embeddings.append(response['embedding'])

embeddings_matrix = np.array(embeddings)
np.save("embeddings.npy", embeddings_matrix)
