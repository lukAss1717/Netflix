# Script, welches das Netflix-Datenset aus KAGGLE einliest und verschiedene Datenbereinigungs- und Transformationsschritte durchführt 
import pandas as pd

# Daten einlesen und fehlende Werte behandeln
netflix_df = pd.read_csv('netflix_titles.csv', parse_dates=['date_added'])
netflix_df['country'] = netflix_df['country'].fillna(netflix_df['country'].mode()[0])
netflix_df = netflix_df.dropna(subset=['date_added', 'rating', 'duration'])

# Alterseinstufungen anpassen
age_mapping = {'TV-MA': 'R', 'TV-14': 'PG-13', 'TV-PG': 'PG', 'TV-Y': 'PG', 'TV-Y7':'PG',
       'TV-G':'G', 'TV-Y7-FV': 'PG', 'UR':'NR'}
netflix_df['rating'] = netflix_df.rating.apply(lambda x: age_mapping[x] if x in age_mapping else x)

# Dauer der Shows in Minuten extrahieren
netflix_df['duration_t'] = netflix_df['duration'].str.extract('(\d+)').astype(int)

# Aktuelles Datum und Datum vor einem Jahr berechnen
today = netflix_df.date_added.max()
one_year_ago = pd.to_datetime(today.replace(year=today.year - 1))

# Datensätze für das letzte Jahr filtern
netflix_df['date_added_dt'] = pd.to_datetime(netflix_df['date_added'])
last_year_df = netflix_df[netflix_df['date_added_dt'] < one_year_ago]

# Daten von TMDB für Serien und Filme einlesen und mit Netflix-Daten verbinden
series_tmbd_df = pd.read_csv('series_tmdb_data.csv')
movies_tmbd_df = pd.read_csv('movie_tmdb_data.csv')
nf_tmdb_series = pd.merge(netflix_df, series_tmbd_df, left_on="title", right_on="netflix_title", how='left')
nf_tmdb = pd.merge(nf_tmdb_series, movies_tmbd_df, left_on='title', right_on='netflix_title', how='left')

# Spalten mit Daten aus TMDB auffüllen
columns_to_fill = [value for value in nf_tmdb.columns if '_y' in value][1:]
columns_to_use = [value for value in nf_tmdb.columns if '_x' in value]
for column in columns_to_fill:
    nf_tmdb[column] = nf_tmdb[column].fillna(nf_tmdb[column[:-2] + '_x'])

# Überflüssige Spalten entfernen
nf_tmdb = nf_tmdb.drop([col for col in columns_to_use], axis=1)
nf_tmdb = nf_tmdb.rename(columns={col: col[:-2] for col in columns_to_fill})
nf_tmdb = nf_tmdb.drop(["Unnamed: 0", "adult", "origin_country", "original_name", "first_air_date",
            "name","genre_ids","id","original_language","original_title","overview","release_date","video", "title"], axis=1)

# Länder als binäre Variablen codieren
binary_country = nf_tmdb['country'].str.get_dummies(sep=',')
nf_tmdb = nf_tmdb.join(binary_country)

# Genres extrahieren und als binäre Variablen codieren
nf_tmdb['genre'] = nf_tmdb['listed_in'].apply(lambda x :  x.replace(' ,',',').replace(', ',',').split(','))
all_genre = list()
for i in range(nf_tmdb.shape[0]):
    for index, j in enumerate(nf_tmdb.iloc[i].genre):
        all_genre.append(nf_tmdb.iloc[i].genre[index])
nf_tmdb.genre = [','.join(map(str, l)) for l in nf_tmdb['genre']]
binary_genre = nf_tmdb['genre'].str.get_dummies(sep=',')
nf_tmdb = nf_tmdb.join(binary_genre)

# Daten als CSV-Datei speichern
nf_tmdb.to_csv('test_prepared_netflix.csv', sep='\t', encoding='utf-8', index=False)
