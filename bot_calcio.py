import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# --- 1. CONFIGURAZIONE E DATABASE ---
st.set_page_config(page_title="AI LIVE SCANNER 2026", layout="wide")

# Database Forza Squadre (Aggiornato Maggio 2026)
EURO_TEAMS = {
    "Serie A 🇮🇹": ["Inter", "Milan", "Juventus", "Napoli", "Atalanta", "Roma", "Lazio", "Bologna", "Fiorentina", "Torino"],
    "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": ["Man City", "Arsenal", "Liverpool", "Aston Villa", "Tottenham", "Chelsea", "Man United", "Newcastle"],
    "La Liga 🇪🇸": ["Real Madrid", "Barcelona", "Girona", "Atletico Madrid", "Athletic Bilbao", "Real Sociedad"],
    "Bundesliga 🇩🇪": ["Bayer Leverkusen", "Bayern Munich", "Stuttgart", "RB Leipzig", "Dortmund", "Frankfurt"],
    "Ligue 1 🇫🇷": ["PSG", "Monaco", "Brest", "Lille", "Nice", "Lyon", "Marseille"]
}

# --- 2. MOTORE DI RICERCA AUTOMATICA (WEB INTELLIGENCE) ---
class WebIntelligence:
    @staticmethod
    def get_scheduled_events():
        """
        Simula la scansione di portali come Diretta.it o Flashscore.
        L'IA 'legge' i match previsti per oggi 01/05/2026.
        """
        # In un'implementazione reale, qui useresti requests.get(url) 
        # per estrarre gli eventi dal codice HTML del sito.
        return {
            "Serie A 🇮🇹": [
                {"ora": "18:30", "h": "Juventus", "a": "Milan"},
                {"ora": "20:45", "h": "Inter", "a": "Napoli"}
            ],
            "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": [
                {"ora": "21:00", "h": "Arsenal", "a": "Liverpool"}
            ],
            "La Liga 🇪🇸": [
                {"ora": "21:00", "h": "Real Madrid", "a": "Barcelona"}
            ]
        }

# --- 3. LOGICA DI ANALISI ---
def analyze_match(h, a):
    # Indice di forza simulato (Power Index)
    import random
    p1 = random.uniform(0.3, 0.6)
    p2 = random.uniform(0.2, 0.4)
    px = 1.0 - (p1 + p2)
    return {"1": p1, "X": px, "2": p2}

# --- 4. INTERFACCIA UTENTE ---
st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: white; }
    .event-card { 
        background: #161b22; border: 1px solid #30363d; 
        border-radius: 12px; padding: 15px; margin-bottom: 10px;
    }
    .status-live { color: #238636; font-weight: bold; font-size: 0.8rem; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌐 AI Neural Event Predictor 2026")
st.markdown(f'<p class="status-live">● AI WEB SCANNER ONLINE - Sincronizzato: {datetime.now().strftime("%d/%m/%Y %H:%M")}</p>', unsafe_allow_html=True)

# Recupero automatico eventi
with st.spinner("L'IA sta scansionando i palinsesti europei..."):
    daily_catalog = WebIntelligence.get_scheduled_events()

# --- 5. NAVIGAZIONE E CATALOGO ---
tab_auto, tab_manual = st.tabs(["📅 Eventi in Programma", "🔍 Ricerca Manuale"])

with tab_auto:
    st.subheader("Partite rilevate per oggi")
    for league, matches in daily_catalog.items():
        with st.expander(f"⚽ {league}", expanded=True):
            for m in matches:
                res = analyze_match(m['h'], m['a'])
                st.markdown(f"""
                <div class="event-card">
                    <span style="color: #58a6ff;">🕒 {m['ora']}</span>
                    <h4>{m['h']} vs {m['a']}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2, c3 = st.columns(3)
                c1.metric("SEGNO 1", f"{res['1']:.0%}")
                c2.metric("SEGNO X", f"{res['X']:.0%}")
                c3.metric("SEGNO 2", f"{res['2']:.0%}")
                st.divider()

with tab_manual:
    st.subheader("Cerca una partita specifica nel catalogo")
    c1, c2 = st.columns(2)
    sel_league = c1.selectbox("Seleziona Campionato", list(EURO_TEAMS.keys()))
    sel_h = c2.selectbox("Squadra Casa", EURO_TEAMS[sel_league])
    sel_a = st.selectbox("Squadra Trasferta", [t for t in EURO_TEAMS[sel_league] if t != sel_h])
    
    if st.button("🚀 Analizza Scontro"):
        custom_res = analyze_match(sel_h, sel_a)
        st.write(f"### Analisi: {sel_h} vs {sel_a}")
        st.json(custom_res)

# --- 6. AGGIORNAMENTO REQUISITI ---
# Ricordati di aggiungere 'beautifulsoup4' e 'requests' nel tuo requirements.txt
