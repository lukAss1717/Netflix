import streamlit as st

# Seitentitel und Beschreibung festlegen
st.title("💡 :red[Stolpersteine & Lerneffekte]")

st.markdown("""
            ## Herausforderungen
            - Identifizierung des Datensatzes: Suche nach einem geeigneten Datensatz, der eine Vorverarbeitung erfordert, um den Lerneffekt zu gewährleisten.
            """)

# Bild 1: Identifizierung des Datensatzes
image1_path = "images/kaggle.png"
st.image(image1_path, width=300)
st.caption("""[Databuff, CC BY-SA 3.0](https://creativecommons.org/licenses/by-sa/3.0), via Wikimedia Commons""")

st.markdown("""
            - Verständnis der Benutzerperspektive: Sich in die Lage potenzieller Benutzer versetzen, um wertvolle Erkenntnisse für sie zu identifizieren.
            """)

# Bild 2: Verständnis der Benutzerperspektive
image2_path = "images/views.png"
st.image(image2_path, width=300)
st.caption("""Bild von [Yvette W](https://pixabay.com/de/users/wallusy-7300500/?utm_source=link-attribution&amp;utm_medium=referral&amp;utm_campaign=image&amp;utm_content=6246450) auf [Pixabay](https://pixabay.com/de//?utm_source=link-attribution&amp;utm_medium=referral&amp;utm_campaign=image&amp;utm_content=6246450)""")

st.markdown("""
            - Technische Umsetzung: Arbeit mit API-Schnittstellen zur Anreicherung des Datensatzes und Überwindung von Herausforderungen wie unterschiedlichen Benennungskonventionen.
            """)

# Bild 3: Technische Umsetzung
image_url_3 = "images/tmdb.png"
st.image(image_url_3, width=300)
st.caption("""[TMDB Logo](https://www.themoviedb.org/about/logos-attribution), von TMDB""")


st.markdown("""
            ---
            ## Learnings
            - Standardisierter Prozess: Anwendung eines strukturierten Ansatzes mit Feedbackschleifen, wie dem CRISP-DM-Modell, für eine effiziente Projektdurchführung.
            """)

# Bild 4: Standardisierter Prozess
image_url_4 = "images/CRISP-DM.png"
st.image(image_url_4)
st.caption("""[CRISP-DM Diagramm](https://www.datascience-pm.com/crisp-dm-2/), inspiriert von Wikipedia""")

st.markdown("""
            - Dynamische Datenbasis: Integration von Benutzereingaben zur Anpassung und Modifikation des Datensatzes, um Relevanz sicherzustellen und die Benutzererfahrung zu verbessern.
            """)

# Bild 5: Dynamische Datenbasis
image_url_5 = "images/st_pandas.png"
st.image(image_url_5, width=300)
st.caption("""[streamlit-pandas 0.0.9](https://pypi.org/project/streamlit-pandas/), von pypi.org""")


st.markdown("""
            - Analytische Denkweise: Anwendung von kritischem Denken und Hinterfragen bei der Erstellung von Ansichten in einem Dashboard.
            """)

# Bild 6: Analytische Denkweise
image_url_6 = "images/analytics.png"
st.image(image_url_6, width=400)
st.caption("""Bild von [storyset](https://www.freepik.com/free-vector/data-inform-illustration-concept_6195525.htm#query=analytics&position=4&from_view=search&track=sph), auf Freepik""")

st.sidebar.success("Wähle eine Seite aus")
st.sidebar.markdown('''
---
🛠️ Created by Group 1. 
''')

# Streamlit Footer auslenden 
hide_streamlit_style = """<style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)