#imports 
import streamlit as st
import pandas as pd
import numpy as np 
import plotly.express as px  
import plotly.graph_objs as go
import matplotlib.pyplot as plt 
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')

# einlesen der Primärdatenquelle (in data_preperation.ipynb erzeugtes csv) 
df = pd.read_csv('prepared_netflix.csv', parse_dates=['date_added'], delimiter='\t')
netflix_df = df

# setzt die App auf Fullscreeen und die Sidebar auf offen als Standard 
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

# liest das css file ein für global Styles 
with open('stlye.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Seitentitel
st.title("📈 :red[ Dashboard]")

### Sidebar
# Überschrift
st.sidebar.header('`Dashboard` Filme & Serien')
# Netflix Logo
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/7/7a/Logonetflix.png", width=200)
## Filter 1 
# Unterüberschrift
st.sidebar.subheader('Inhaltstyp')
# Radiobutton um auszuwählen ob Serien oder Filme analysiert werden wollen 
type_selected = st.sidebar.radio(
        "Welche Art von Inhalt willst du analysieren?",
        netflix_df.type.unique(), 
        horizontal=True
    )
# aktualisieren der Datenbasis 
netflix_df = netflix_df[netflix_df["type"] == type_selected]

## Filter 2 
# extrahieren der verschiedenen Genre für den aktuellen Zustand des DF 
genre_only = netflix_df.iloc[:,217:]
genre_list = genre_only.columns[(genre_only != 0).any()]
# Unterüberschrift 
st.sidebar.subheader('Genre')
# multiauswahl Dropdownfeld um nach Genre zu selektieren 
genre_selected = st.sidebar.multiselect('Welches Genre willst du betrachten?', options=genre_list)
# aktualisieren der Datenbasis wenn ein Genre ausgewählt wurde 
if  len(genre_selected) == 0:
    netflix_df = netflix_df 
else: 
    netflix_df = netflix_df[(netflix_df[genre_selected] > 0).any(axis=1)]

## Filter 3 
# Unterüberschrift
st.sidebar.subheader('Altersbeschränkung')
# Beschreibung
st.sidebar.write('Grenze die Resultate anhand der Altersbeschränkung ein:')

# Checkbox für alle möglichen Altersbeschränkungen 
g_selected = st.sidebar.checkbox("alle Altersgruppen")
pg_selected = st.sidebar.checkbox("ab 6 Jahren")
pg_13_selected = st.sidebar.checkbox(" ab 13 Jahren")
r_selected = st.sidebar.checkbox("ab 16 Jahren")
nc_17_selected = st.sidebar.checkbox("ab 18 Jahren")
nr_selected = st.sidebar.checkbox("unbewertet")
# mapping zwischen Checkbox und Altersbeschränkung im Dataset 
rating_dict = {"G": g_selected, 
                "PG": pg_selected, 
                "PG-13": pg_13_selected, 
                "R": r_selected,
                "NC-17": nc_17_selected,
                "NR": nr_selected}
# Liste mit ausgewählten Altersbeschränkungen 
rating_list = [key for key, value in rating_dict.items() if value == True]
# aktualisieren der Datenbasis wenn mindestens eine ALtersbeschränkung ausgewählt wurde 
if (len(rating_list) != 0): 
    # Datenbasis wird aktualisiert damit nur mehr Einträge vorhanden sind die in der Rating Spalte einen der ausgewählten Altersbeschränkungen entsprechen 
    netflix_df = netflix_df[netflix_df['rating'].isin(rating_list)]
    #wenn nichts ausgewählt ist soll es sich so verhalten als wären alle ausgewählt und keine Eingrenzung vorgenommen worden sein 
else: 
    netflix_df = netflix_df[netflix_df['rating'].isin(list(rating_dict.keys()))]

## Filter 4
# Unterüberschrift 
st.sidebar.subheader('Erscheinungsjahr')

# extrahieren aller Jahre in der Datenbasis um den Slider zu erstellen 
years = [str(x) for x in np.sort(df['release_year'].unique())]
from_year =  str(df['release_year'].min())
to_year =  str(df['release_year'].max())

# Slider für das selektieren der Elemente basierend auf ihren Entscheidungsjahr 
selected_start_year, selected_end_year = st.sidebar.select_slider('Grenze die Resultate basierend auf dem Erscheinungsjahr ein:',options = years, value = (from_year, to_year))

# aktualisieren der Datenbasis, basierend auf ausgewählte min und max input des Users 
netflix_df = netflix_df[(netflix_df['release_year'] >= int(selected_start_year)) & (netflix_df['release_year'] <= int(selected_end_year))]

# Zustand der Datenbasis vor einem Jahr selektieren um später dadurch jährliche Änderungsraten anzuzeigen 
# da keine Realtimdaten zur Verfügung standen, wurde angenommen. dass der letzte Tag im Dataset den heutigen Tag darstellt 
today = netflix_df.date_added.max()
one_year_ago = pd.to_datetime(today.replace(year=today.year - 1))
netflix_df['date_added_dt'] = pd.to_datetime(netflix_df['date_added'])
last_year_df = netflix_df[netflix_df['date_added_dt'] < one_year_ago]

# überprüfen ob movies oder tv shows ausgewählt wurden um die korrekte Maßeinheit anzuzeigen 
if type_selected == "Movie": 
    type_name = "Filme"
    type_measure = "Min"
else: 
    type_name = "Serien"
    type_measure = "Staffeln" 
change_avg_duration = str(round((netflix_df.duration_t.mean() - last_year_df.duration_t.mean()) / netflix_df.duration_t.mean(),2)) + " " + "%"

# Creator Note und Alter des Ursprungsdatasets  
st.sidebar.markdown(f'''
---
🛠️ Created by Group 1. \n
📅 Datenzustand: {today}
''')

#---------------
### Abschnitt 1 
## Data Preperation 
# Änderungsrate der Elementanzahl im Vergleich zum Vorjahr 
change_count = str(round((netflix_df.shape[0] - last_year_df.shape[0]) / netflix_df.shape[0],2)) + " " + "%"
# Ermittlung des User Ratings der selektierten Elemente im Durchschnitt 
percentage_value = round(netflix_df['vote_average'].mean() * 10,2)
progress_label = f"{percentage_value}%"

## Design 
# Abschnittstitel 
st.markdown('### :red[KPIs]')
# Layout in drei gleichen Spalten 
col1, col2, col3 = st.columns(3)
# Metrik, welche die Gesamtanzahl an Titel in der Selektion anzeigt 
col1.metric("Gesamtanzahl",  str(netflix_df.shape[0]) + " " + type_name, change_count, help="Im Vergleich zum Vorjahr")
# Metrik, welche die durschn. Länge der Titel in der Selektion anzeigt 
col2.metric("Durschnittliche Länge", str(round(netflix_df.duration_t.mean(),2)) + " " + type_measure, change_avg_duration, help="Im Vergleich zum Vorjahr")
with col3:
    # Metrik, welche das durschnittliche User Rating anzeigt und zusätzlich eine visuelle Repräsentation der % Zahl als Balken wiedergibt 
    st.metric("Avg. User Rating", progress_label, help="Daten erhoben von TMDB")
    progress_bar = st.progress(percentage_value / 100.0)
    progress_bar.progress(percentage_value / 100.0)
st.divider()

### Abschnitt 2 
## Data Preperation 
# alle Länder in eine Liste (zuvor Spalten im Df)
countries = netflix_df.columns[20:216]
# neues Df das alle Länderspalten summiert und in ein Df verwandelt 
# (die binären Spalten der Länder waren notwendig da Filme/Serien in mehreren Ländern produziert werden können)
geo = netflix_df[countries].sum().to_frame() 
# der unbeannten Spalte einen Namen geben 
geo_df = geo.rename(columns={0: 'Produktionen'})
# Erstellung des Weltkartenplots mit Plotly Express
fig = px.choropleth(
    geo_df,
    locations=geo_df.index,
    locationmode='country names',
    color=geo_df.Produktionen,
    title=f'Anzahl an produzierten {type_name} pro Land',
    scope='world',
    color_continuous_scale=[
        [0.0, '#4d0000'],
        [0.2, '#800000'],
        [0.4, '#b30000'],
        [0.6, '#e60000'],
        [0.8, '#ff1a1a'],
        [1.0, '#ff3333']
    ],
)

## Design 
st.markdown('### :red[geographische Analyse]')
fig.update_layout(title_font_size=20)
# Formatierung des Weltkartenplots 
fig.update_geos( showland=True, landcolor="darkgrey", oceancolor="black")
# Weitere Formatierungen des Plots aber auf anderer Ebene 
fig.update_layout(
    title=f'Anzahl an produzierten {type_name} pro Land',
    margin=dict(l=0, r=0, t=50, b=0),
    geo=dict(
        showframe=False,
        showcoastlines=False,
        projection_type='natural earth'
    ),
    # Formatierung der Legende 
    coloraxis_colorbar=dict(
        title="Anzahl Produktionen",
        thickness=20,
        len=0.8,
        y=0.5,
        yanchor='middle', 
        x=1.05
    ),
    template='plotly_dark'
)
# hinzufügen des Weltkartenplots in das App-Interface 
st.plotly_chart(fig, theme="streamlit", use_container_width=True)
st.divider()

### Abschnitt 3
## Data Preperation - Linienplot Portfolio Entwicklung
# neues DF, das nach den Tagen gruppiert und die kumulierte Summe der Anzahl an Titel wiedergibt 
time_df = netflix_df.groupby(by=['date_added_dt']).count().cumsum()

## Data Peperation - Altersanalyse 
t5_countries_grouped = netflix_df.groupby('country')[['show_id']].count().sort_values(by='show_id',ascending=False).reset_index()[:5]
t5_series = t5_countries_grouped['country']
top5_countries = netflix_df.loc[netflix_df['country'].isin(t5_series)]
top5_countries['nf_release_year'] = top5_countries['date_added'].dt.year
diff_released_added = top5_countries.groupby('country')['release_year','nf_release_year'].mean().round()
diff_released_added['diff'] = diff_released_added['nf_release_year'] - diff_released_added['release_year'] 
diff_released_added_ordered = diff_released_added.sort_values('diff')

## Design - Linienplot 
st.markdown('### :red[zeitliche Analyse]')
# Erstellung Linienplot, welche die Anzahl der insgesamten Titel über die Zeit hinweg auf Netflix wiederspiegelt 
fig = go.Figure()
fig.add_trace(go.Scatter(x=time_df.index, y=time_df['show_id'], mode='lines'))
# Formatierung des Linienplots 
fig.update_layout(title=f"Entwicklung des Portfolios ({type_name})", title_font_size=20, xaxis_title='Datum', yaxis_title=f'{type_name}-Auswahl erweitert')
fig.update_traces(line_color='#b20710')

# Gliederung des Layouts in zwei Spalten die unterschiedlich groß sind 
c1, c2 = st.columns((6,4))
with c1:
    # hinzufügen des Linienplots in die linke Spalte des App-Interface
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

## Design - Altersanalyse 
# Erstellung einer leeren plotly figure 
fig = go.Figure()
# Hinzufügen eines Scattercharts der pro Land einen Punkt hinzufügt für das durchschnittliche Erscheinungsjahr eines Filmes oder einer Serie 
fig.add_trace(go.Scatter(x=diff_released_added_ordered['release_year'], y=diff_released_added_ordered.index, mode='markers', 
                        marker=dict(color='grey', size=10), name='Erscheinungsjahr'))
# Hinzufügen eines Scattercharts der pro Land einen Punkt hinzufügt für das durchschnittliche Erscheinungsjahr auf NETFLIX eines Filmes oder einer Serie 
fig.add_trace(go.Scatter(x=diff_released_added_ordered['nf_release_year'], y=diff_released_added_ordered.index, mode='markers',
                        marker=dict(color='#b20710', size=10), name='hinzugefügt NF'))
# Hinzufügen eines Barcharts der beide Scattercharts verbindet und so das Durchschnittsalter eines Filmes/ einer Serie auf NETFLIX wiedergibt 
fig.add_trace(go.Bar(x=diff_released_added_ordered['diff'], y=diff_released_added_ordered.index, base=diff_released_added_ordered['release_year'], orientation="h", width=0.01, marker_color='#999999', showlegend=False))

# Formatierung der Figure 
fig.update_layout(
    # Hinzufügen eines Variablen Titels je nachdem ob Film oder Serie in der Filterauswahl getroffen wurde 
    title=f"Durchschnittsalter der {type_name}",
    title_font_size=20,
    yaxis=dict(
        tickmode='array',
        showgrid=False,
        tickvals=diff_released_added_ordered.index,
        ticktext=diff_released_added_ordered.index,
        side='right'
    ),
    margin=dict(t=80, l=10, r=10, b=10),
    # Formatierung der Legende 
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        entrywidth=85
    ),
    xaxis=dict(showgrid=False)
)
with c2: 
    # hinzufügen des Altersanalysenplots in der rechten Spalte des App-Interface
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
st.divider()

### Abschnitt 4 

## Data Preperation linke Spalte 
text = ' '.join(netflix_df['netflix_title'].dropna().values)
# Entfernung von üblichen Stopwörtern aus dem Korpus mittels NLTK wie z.B. of, the, etc.
stop_words = set(stopwords.words('english'))
# ebenfalls "&" und "-" als Stopwörter definieren
stop_words.update("&","-")
# Wörter aus dem Titel hinzufügen zu einer Liste insofern sie nicht in den Stopwörter vorhanden sind 
words = [word.lower() for word in text.split() if word.lower() not in stop_words]
# Berechnung der Frequenz jedes Wortes in der Liste
freq_dict = {}
for word in words:
    freq_dict[word] = freq_dict.get(word, 0) + 1
# Erstellung eines DF mit den Frequenzen jedes Wortes 
freq_df = pd.DataFrame(list(freq_dict.items()), columns=['word', 'freq'])
# Sortierung nach Frequenzen und Auswahl der häufigsten 10 Wörter
top_words = freq_df.sort_values('freq', ascending=False).head(10)

## Data Preperation rechte Spalte 
# alle Beschreibungen zu einem großen Text zusammenfassen
text = ' '.join(netflix_df.description.dropna().values)
# laden einer zusätzlichen Farbpalette 
red_colormap = plt.cm.get_cmap('Reds')
# Erstellung der Wordcloud mit eigener Library 
wordcloud = WordCloud(background_color='black', colormap=red_colormap).generate(text)

## Design linke Spalte - Treemap 
st.markdown('### :red[inhaltiche Analyse]')
# Hinzufügen einer benutzerdefinierten Colorscale (rot)
color_scale = ['#FFCDD2', '#EF9A9A', '#E57373', '#EF5350', '#F44336', '#E53935', '#D32F2F', '#C62828', '#B71C1C', '#8B0000']
# Erstellung der Treemap mit Plotly 
fig = px.treemap(top_words, path=['word'], values='freq', title='Häufigsten Wörter im Titel',  color_discrete_sequence=color_scale)
fig.update_layout(title_font_size=20)
# Layout in 2 gleichgroßen Spalten
c1, c2 = st.columns((5, 5))
with c1: 
    # Hinzufügen der Treemap in der linken Spalte
    st.plotly_chart(fig, use_container_width=True)

## Design rechte Spalte - Wordcloud 
# Formatierung der Wordcloud zu einem plotly Plot 
wordcloud_fig = px.imshow(wordcloud.to_array(), color_continuous_scale='Reds', title='Häufigsten Wörter in der Beschreibung')
# Formatierung des Plots 
wordcloud_fig.update_layout(
    title_font_size=20,
    xaxis=dict(
        showticklabels=False,
        showgrid=False,
        zeroline=False
    ),
    yaxis=dict(
        showticklabels=False,
        showgrid=False,
        zeroline=False
    ),
    margin=dict(l=0, r=0, t=40, b=0),
    # deaktievierung des Hovermodes, da er nur Koordinaten im Bild/Matrix anzeigt 
    hovermode=False
    )
with c2:
    #Hinzufügen der Wordcloud in die rechte Spalte 
    st.plotly_chart(wordcloud_fig, use_container_width=True)
st.divider()


### Abschnitt 5 

## Data Preperation
# globale maxima finden für Popularität 
most_pop_pop_general = df.iloc[netflix_df['popularity'].idxmax()]['popularity']
# Zurücksetzen des Indexes nach der Filterung 
netflix_df = netflix_df.reset_index()
# Titel, Pfad zum Cover und Popularitätsscore des populärsten Filmes/Serie jeweils einer Variable zuordnen 
most_pop_title = netflix_df.iloc[netflix_df['popularity'].idxmax()]['netflix_title']
most_pop_cover = netflix_df.iloc[netflix_df['popularity'].idxmax()]['poster_path']
most_pop_pop = netflix_df.iloc[netflix_df['popularity'].idxmax()]['popularity']
# durchschnittliche Popularität der Auswahl an Datensätzen bestimmen 
avg_pop = netflix_df['popularity'].mean()
# Director und Cast des populärsten Titels einer Variable zuweisen 
most_pop_director = netflix_df.iloc[netflix_df['popularity'].idxmax()]['director']
most_pop_cast = list() 
if isinstance(netflix_df.iloc[netflix_df['popularity'].idxmax()]['cast'], str): 
    # Transformation des Casts in eine Liste 
    most_pop_cast = netflix_df.iloc[netflix_df['popularity'].idxmax()]['cast'].split(',')

## Design 
st.markdown (f"### :red[Populärster {type_name[:-1]}]", help="keine Garantie für Datenrichtigkeit, da Fuzzy Matching verwendet wird um zweite Datenquelle zu durchsuchen")
col1, col2, col3 = st.columns((2,4,2))

# Spalte 1
with col1: 
    #Hinzufügen des Covers und Namen des Titels zu Spalte 1
    st.markdown(f'## {most_pop_title}')
    image_url = "https://image.tmdb.org/t/p/original/" + most_pop_cover
    st.image(image_url, caption=f"{type_name[:-1]} Cover ", width=250)

# Spalte 2
with col2: 
    #Hinzufügen des Directors zu Spalte 2 
    st.markdown ("### :red[Produziert von]")
    st.metric("Regisseur", most_pop_director)
    #Hinzufügen des Casts zur Spalte 2 wobei hier 3 Schauspieler fix gezeigt werden und die anderen in einem ausklappbaren Element 
    st.markdown ("### :red[Cast]",unsafe_allow_html=True)
    if most_pop_cast: 
        for count, person in enumerate(most_pop_cast): 
            st.metric("Schauspieler", person)
            if count >= 2: 
                with st.expander("Weitere Mitwirkende"):
                    for i in most_pop_cast[3:]: 
                        st.metric("Schauspieler", i)
                break 
            else: 
                continue
    else: 
        # wenn der Cast unbekannt ist wird diese Message platziert 
        st.markdown ("#### keine Daten vorhanden 🥹")

# Spalte 3 
with col3: 
    # Erstellung einer Gauge Visualisierung innerhalb eines plotly plots 
    fig = go.Figure(go.Indicator(
    # Modus der Methode auswählen 
    mode = "gauge+number",
    # Einsetzen des Popularitätsscores der zuvor ermittelt wurde 
    value = most_pop_pop,
    # Charakteristika definieren (von, bis, Farbe, zusätzliche Indikationen)
    gauge = {
        'axis': {'range': [None, most_pop_pop_general]},
        'steps' : [
            {'range': [0, 100], 'color': "#1a1a1a"}],
        'threshold' : {'line': {'color': "white", 'width': 4}, 'thickness': 0.75, 'value': avg_pop},
        'bar': {'color': "red"}
    }))
    # Zusätzliche Formatierung für das Spacing 
    fig.update_layout(
    margin=dict(l=20, r=20, t=50, b=20),  
    # Hinzzfügen des Titels 
    title=dict(text="Popularity Score", x=0.5, y=0.9, font=dict(size=20, color="#FFFFFF"), xanchor="center"),  
)
    # Hinzufügen der Gauge Visualisierung zu Spalte 3 
    st.plotly_chart(fig, use_container_width=True)

# Streamlit Footer auslenden 
hide_streamlit_style = """<style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)