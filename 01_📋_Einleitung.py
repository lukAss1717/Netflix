import streamlit as st
import pandas as pd

# die App in eine Multipage App verwandeln 
st.set_page_config(page_title = "This is a Multipage WebApp", layout="wide")
st.sidebar.success("Wähle eine Seite aus")

# Laden des Datasets 
df = pd.read_csv('prepared_netflix.csv', parse_dates=['date_added'], delimiter='\t')

# Projekt Titel und Beschreibung 
st.image("https://upload.wikimedia.org/wikipedia/commons/7/7a/Logonetflix.png", width=400 )
st.title(":red[Visualisierungsprojekt - Einleitung]")
st.markdown("""
            ## 🏛️ Ausgangslage
            In diesem Projekt liegt der Fokus auf dem "Netflix Shows" Datensatz. Der Datensatz enthält Informationen über verschiedene TV-Shows und Filme, die auf Netflix verfügbar sind. Er bietet eine Vielzahl von Variablen,
            wie den Titel, das Erscheinungsjahr, den Regisseur, das Land und vieles mehr.
            
            ## 📋 Dataset-Beschreibung
            Der "Netflix Shows" Datensatz enthält die folgenden Spalten:
            - show_id: Eindeutige ID der Show
            - type: Typ der Show (TV-Show oder Film)
            - title: Titel der Show
            - director: Regisseur der Show
            - cast: Darsteller der Show
            - country: Land der Produktion
            - date_added: Datum, an dem die Show zu Netflix hinzugefügt wurde
            - release_year: Jahr der Veröffentlichung der Show
            - rating: Altersfreigabe der Show
            - duration: Dauer der Show
            - listed_in: Kategorien/Tags, denen die Show zugeordnet ist
            - description: Kurze Beschreibung der Show
            
            ## 🏁 Ziel des Projekts
            Das Ziel dieses Projekts besteht darin, ein interaktives Dashboard zu entwickeln, das den Benutzern ermöglicht,
            den Netflix-Korpus nach verschiedenen Kriterien zu durchsuchen und zu filtern. Dazu gehören die Suche nach bestimmten
            Genres, Ländern, Regisseuren, Darstellern, Altersfreigaben und vielem mehr. Das Dashboard soll visuelle Darstellungen
            der Daten bieten, um Trends und Muster im Netflix-Korpus zu identifizieren.
            """)

# Dataset Überblick
st.header("🔍 Datensatzüberblick")
st.write("Anzahl der Datensätze:", df.shape[0])
st.write("Spalten im Datensatz:", df.shape[1])
st.write("Beispielhafte Datensatzvorschau:")
st.dataframe(df.head())

st.sidebar.markdown('''
---
🛠️ Created by Group 1.
''')
# Streamlit Footer ausblenden 
hide_streamlit_style = """<style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)