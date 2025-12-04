import pandas as pd

# läs data
df = pd.read_csv("imdb_tvshows.csv")

features = ['About', 'Genres', 'Actors']
for feature in features:
    df[feature] = df[feature].fillna('')

def combine_features(row):
    return f"{row['About']} {row['Genres']} {row['Actors']}"

# Applicera funktionen
df['combined_features'] = df.apply(combine_features, axis=1)

# Spara den nya filen som du sedan laddar i din huvudapp
df.to_csv("processed_tvshows.csv", index=False)
print("Data förbehandlad och sparad!")