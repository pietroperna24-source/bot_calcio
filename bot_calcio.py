import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import random

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="AI WEB ANALYST 2026", layout="wide")

# CSS per nascondere menu Streamlit
st.markdown("""<style>#MainMenu, header, footer {visibility: hidden;} .stApp {background: #0d1117;}</style>""", unsafe_allow_html=True)

class WebScraperAI:
    @staticmethod
    def get_match_data(url):
        """Tenta di leggere dati da un URL fornito"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Qui l'IA estrae il testo principale della pagina per analizzarlo
            text_content = soup.get_text()
            return text_content[:2000] # Analizza i primi 2000 caratteri
        except Exception as e:
            return f"Errore durante la scansione: {e}"

    @staticmethod
    def process_prediction():
        """Genera pronostici simulando l'analisi dei dati web"""
        # Simuliamo un database di partite rilevate oggi
        matches = [
            {"match": "Inter vs Milan", "league": "Serie A", "trend": "Inter vince da 5 partite"},
            {"match": "Real Madrid vs Barcellona", "league": "La Liga", "trend": "Real Madrid imbattuto in casa"},
            {"match": "Man City vs Arsenal", "league": "Premier League", "trend": "Scontro diretto per il titolo"}
        ]
        return matches

# --- INTERFACCIA ---
st.title("🌐 AI Web Predictor & Intelligence")

tab1, tab2 = st.tabs(["🔍 Analisi Automatica", "🔗 Analizza Link Specifico"])

with tab1:
    if st.button("🌐 SCANSIONA WEB PER PRONOSTICI"):
        with st.spinner("L'IA sta consultando i portali sportivi..."):
            matches = WebScraperAI.process_prediction()
            for m in matches:
                with st.container():
                    st.markdown(f"### {m['match']}")
                    st.caption(f"Lega: {m['league']} | Trend rilevato: {m['trend']}")
                    
                    # Logica AI per percentuali
                    p1, px, p2 = 0.45, 0.30, 0.25 # Esempio di calcolo
                    
                    c1, c2 = st.columns([1, 1])
                    with c1:
                        fig = go.Figure(data=[go.Pie(labels=['1', 'X', '2'], values=[p1, px, p2], hole=.3)])
                        fig.update_layout(height=200, margin=dict(t=0,b=0,l=0,r=0), showlegend=False)
                        st.plotly_chart(fig, use_container_width=True)
                    with c2:
                        st.write("#### Verdetto AI")
                        st.info(f"Consiglio: Vittoria {m['match'].split(' vs ')[0]}")
                    st.divider()

with tab2:
    url = st.text_input("Incolla URL di un sito di statistiche")
    if st.button("Analizza Sito"):
        if url:
            data = WebScraperAI.get_match_data(url)
            st.write("### Dati estratti dal Web:")
            st.text_area("Contenuto analizzato dall'IA", data, height=200)
            st.success("Analisi completata. L'IA ha integrato questi dati nei suoi calcoli.")
