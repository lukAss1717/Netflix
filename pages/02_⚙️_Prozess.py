import streamlit as st

# Konfiguration der Seite 
st.set_page_config(layout="wide")

# Seitentitel
st.title("⚙️ :red[ Umsetzungsprozess]")

# Bild zur Prozessbeschreibung
st.image("images/process.png", caption="Visualisierungsprojekt Prozessschritte", use_column_width=True)

# weitere Zeilenschlatung für bessere Lesbarkeit
st.markdown("<br><br>", unsafe_allow_html=True)
st.sidebar.success("Wähle eine Seite aus")
st.sidebar.markdown('''
---
🛠️ Created by Group 1. 
''')
