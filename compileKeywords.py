import pandas as pd

df = pd.read_csv("shows.csv")

features = ['rank', 'title', 'year', 'imdb_votes', 'imdb_rating', 'duration', 'genre', 'cast_name', 'director_name', 'storyline']
df_sorted = df[features]

df_sorted.to_csv('sorted_shows.csv')
