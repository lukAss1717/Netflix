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
#loading in the data 
df = pd.read_csv('netflix.csv', parse_dates=['date_added'], delimiter='\t')
netflix_df = df

#sets the global settings for fullscreen and the default layout for the sidebar when webapp is loaded
st.set_page_config(layout='wide', initial_sidebar_state='expanded')

#reads in the css file and uses is to format the webapp 
with open('stlye.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/7/7a/Logonetflix.png", width=200)
#adding various items to the sidebar to control the visualizations  
st.sidebar.header('`Dashboard` Filme & Serien')

st.sidebar.subheader('Inhaltstyp')
type_selected = st.sidebar.radio(
        "Welche Art von Inhalt willst du analysieren?",
        netflix_df.type.unique(), 
        horizontal=True
    )
#update dataframe
netflix_df = netflix_df[netflix_df["type"] == type_selected]
#getting the genre list based on state of list
genre_only = netflix_df.iloc[:,13:55]
genre_list = genre_only.columns[(genre_only != 0).any()]

st.sidebar.subheader('Genre')
genre_selected = st.sidebar.multiselect('Welches Genre willst du betrachten?', options=genre_list)
#update dataframe based on if the movie/series is within the selected sublist of genres 
if  len(genre_selected) == 0:
    netflix_df = netflix_df 
else: 
    netflix_df = netflix_df[(netflix_df[genre_selected] > 0).any(axis=1)]

st.sidebar.subheader('Altersbeschränkung')
st.sidebar.write('Grenze die Resultate anhand der Altersbeschränkung ein:')

g_selected = st.sidebar.checkbox("alle Altersgruppen")
pg_selected = st.sidebar.checkbox("ab 6 Jahren")
pg_13_selected = st.sidebar.checkbox(" ab 13 Jahren")
r_selected = st.sidebar.checkbox("ab 16 Jahren")
nc_17_selected = st.sidebar.checkbox("ab 18 Jahren")
nr_selected = st.sidebar.checkbox("unbewertet")
rating_dict = {"G": g_selected, 
                "PG": pg_selected, 
                "PG-13": pg_13_selected, 
                "R": r_selected,
                "NC-17": nc_17_selected,
                "NR": nr_selected}
rating_list = [key for key, value in rating_dict.items() if value == True]
#online update the dataframe if atleast one age limit was supplied 
if (len(rating_list) != 0): 
    #update dataframe based on if the movie/series is within the selected sublist of genres 
    netflix_df = netflix_df[netflix_df['rating'].isin(rating_list)]
    #wenn nichts ausgewählt ist soll es sich so verhalten als wären alle ausgewählt und keine Eingrenzung vorgenommen worden sein 
else: 
    netflix_df = netflix_df[netflix_df['rating'].isin(list(rating_dict.keys()))]

st.sidebar.subheader('Erscheinungsjahr')
years = [str(x) for x in np.sort(df['release_year'].unique())]
from_year =  str(df['release_year'].min())
to_year =  str(df['release_year'].max())

selected_start_year, selected_end_year = st.sidebar.select_slider('Grenze die Resultate basierend auf dem Erscheinungsjahr ein:',options = years, value = (from_year, to_year))

netflix_df = netflix_df[(netflix_df['release_year'] >= int(selected_start_year)) & (netflix_df['release_year'] <= int(selected_end_year))]

#Berechnen der Änderungsraten von Inhalten 
#die Annahme wurde getroffen da keine Realtimdaten zur Verfügung standen, 
# dass der letzte Tag im Dataset den heutigen Tag darstellt 
today = today = netflix_df.date_added.max()
one_year_ago = pd.to_datetime(today.replace(year=today.year - 1))
netflix_df['date_added_dt'] = pd.to_datetime(netflix_df['date_added'])
last_year_df = netflix_df[netflix_df['date_added_dt'] < one_year_ago]
change_count = str(round((netflix_df.shape[0] - last_year_df.shape[0]) / netflix_df.shape[0],2)) + " " + "%"
#überprüfen ob movies oder tv shows ausgewählt wurden um die korrekte Maßeinheit anzuzeigen 
if type_selected == "Movie": 
    type_name = "Filme"
    type_measure = "Min"
else: 
    type_name = "Serien"
    type_measure = "Staffeln" 
change_avg_duration = str(round((netflix_df.duration_t.mean() - last_year_df.duration_t.mean()) / netflix_df.duration_t.mean(),2)) + " " + "%"

st.sidebar.markdown('''
---
Created by Group 1.
''')

# Main Window Row 1 
st.markdown('### :red[KPIs]')
col1, col2, col3 = st.columns(3)
col1.metric("Gesamtanzahl",  str(netflix_df.shape[0]) + " " + type_name, change_count, help="Im Vergleich zum Vorjahr")
col2.metric("Durschnittliche Länge", str(round(netflix_df.duration_t.mean(),2)) + " " + type_measure, change_avg_duration, help="Im Vergleich zum Vorjahr")
col3.metric("Avg. User Rating", 4.3, "0.5 Sterne", help="Im Vergleich zum Vorjahr")

# bereite die Daten aus dem Dataframe vor für eine geographische Darstellung 
countries = netflix_df.columns[57:]
geo = netflix_df[countries].sum().to_frame() 
geo_df = geo.rename(columns={0: 'Produktionen'})
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

fig.update_geos( showland=True, landcolor="darkgrey", oceancolor="black")
fig.update_layout(
    title=f'Anzahl an produzierten {type_name} pro Land',
    margin=dict(l=0, r=0, t=50, b=0),
    geo=dict(
        showframe=False,
        showcoastlines=False,
        projection_type='natural earth'
    ),
    coloraxis_colorbar=dict(
        title="Anzahl Produktionen",
        thickness=20,
        len=0.8, # adjust the length of the legend
        y=0.5, # center the legend vertically
        yanchor='middle', # anchor the legend to the middle of the plot
        x=1.05 # place the legend to the right of the plot
    ),
    template='plotly_dark'
)
st.divider()
st.markdown('### :red[geographische Analyse]')
st.plotly_chart(fig, theme="streamlit", use_container_width=True)
st.divider()
# Main window Row 3
st.markdown ('### :red[Mitwirkende]')
col1, col2 = st.columns(2)
col1.metric("erfolgreichster Schauspieler", "Liam Hemsworth")
col2.metric("erfolgreichster Regisseur", "Steven Spielberg")


# Main Window Row 3
st.divider()
st.markdown('### :red[zeitliche Analyse]')
time_df = netflix_df.groupby(by=['date_added_dt']).count().cumsum()

# Create plotly figure object
fig = go.Figure()
# Add trace to the figure object
fig.add_trace(go.Scatter(x=time_df.index, y=time_df['show_id'], mode='lines'))
# Customize layout
fig.update_layout(title=f"Entwicklung des Portfolios ({type_name})", title_font_size=20, xaxis_title='Datum', yaxis_title=f'{type_name}-Auswahl erweitert')
fig.update_traces(line_color='#b20710')



c1, c2 = st.columns((6,4))
with c1:
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)
with c2: 
    t5_countries_grouped = netflix_df.groupby('country')[['show_id']].count().sort_values(by='show_id',ascending=False).reset_index()[:5]
    t5_series = t5_countries_grouped['country']
    top5_countries = netflix_df.loc[netflix_df['country'].isin(t5_series)]
    top5_countries['nf_release_year'] = top5_countries['date_added'].dt.year
    diff_released_added = top5_countries.groupby('country')['release_year','nf_release_year'].mean().round()
    diff_released_added['diff'] = diff_released_added['nf_release_year'] - diff_released_added['release_year'] 
    diff_released_added_ordered = diff_released_added.sort_values('diff')

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=diff_released_added_ordered['release_year'], y=diff_released_added_ordered.index, mode='markers', 
                            marker=dict(color='grey', size=10), name='Erscheinungsjahr'))
    fig.add_trace(go.Scatter(x=diff_released_added_ordered['nf_release_year'], y=diff_released_added_ordered.index, mode='markers',
                            marker=dict(color='#b20710', size=10), name='hinzugefügt NF'))

    fig.add_trace(go.Bar(x=diff_released_added_ordered['diff'], y=diff_released_added_ordered.index, base=diff_released_added_ordered['release_year'], orientation="h", width=0.01, marker_color='#999999', showlegend=False))

    fig.update_layout(
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
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

st.divider()

# Display the wordcloud figure in the second column
st.markdown('### :red[inhaltiche Analyse]')
c1, c2 = st.columns((5, 5))
with c1: 

    text = ' '.join(netflix_df['title'].dropna().values)
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    stop_words.update("&","-")
    words = [word.lower() for word in text.split() if word.lower() not in stop_words]
    text = ' '.join(words)

    # Compute the frequency of each word
    freq_dict = {}
    for word in words:
        freq_dict[word] = freq_dict.get(word, 0) + 1

    # Create a dataframe with the word frequencies
    freq_df = pd.DataFrame(list(freq_dict.items()), columns=['word', 'freq'])

    # Sort the dataframe by frequency and take the top 50 words
    top_words = freq_df.sort_values('freq', ascending=False).head(10)

    # Create the treemap
    fig = px.treemap(top_words, path=['word'], values='freq', title='Häufigsten Wörter im Titel',  color_continuous_scale='Reds')

    st.plotly_chart(fig, use_container_width=True)

# Display the tre
with c2:
    # Collect text from the dataframe
    text = ' '.join(netflix_df.description.dropna().values)

    # Create the wordcloud
    red_colormap = plt.cm.get_cmap('Reds')
    wordcloud = WordCloud(background_color='black', colormap=red_colormap).generate(text)

    # Convert the wordcloud to a Plotly figure
    wordcloud_fig = px.imshow(wordcloud.to_array(), color_continuous_scale='Reds', title='Häufigsten Wörter in der Beschreibung')
    wordcloud_fig.update_layout(
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
        hovermode=False
    )
    st.plotly_chart(wordcloud_fig, use_container_width=True)