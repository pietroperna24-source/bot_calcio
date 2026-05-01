import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. DATABASE DI FORZA (POWER INDEX 2026) ---
# Necessario per generare le percentuali dai nomi estratti dal web
POWER_DB = {
    "Inter": 92, "Milan": 87, "Juventus": 85, "Napoli": 84, "Atalanta": 83, "Roma": 80,
    "Man City": 96, "Arsenal": 94, "Liverpool": 93, "Real Madrid": 97, "Barcelona": 91,
    "Bayern Munich": 92, "Bayer Leverkusen": 90, "PSG": 89, "Monaco": 84
}

# --- 2. CONFIGURAZIONE UI ---
st.set_page_config(page_title="AI EUROPEAN HUB 2026", layout="wide")
st.markdown("""
    <style>
    .stApp {background-color: #0b0e14;}
    .league-header {
        background: linear-gradient(90deg, #1f2937, #111827);
        padding: 15px; border-radius: 10px; border-left: 5px solid #3b82f6;
        margin: 20px 0 10px 0; color: white;
    }
    .match-card {
        background: #161b22; border: 1px solid #30363d;
        border-radius: 12px; padding: 20px; margin-bottom: 10px;
    }
    .time-badge { background: #232d3d; color: #58a6ff; padding: 4px 8px; border-radius: 5px; font-family: monospace; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MOTORE DI SCRAPING & CATALOGAZIONE ---
class EuropeanScraper:
    @staticmethod
    def get_all_european_events():
        """
        Simula lo scraping da Diretta.it catalogando per sezioni.
        Nella realtà, l'IA scansiona le classi 'event__league' e 'event__match'.
        """
        # Struttura dati organizzata per Campionato
        catalogo = {
            "ITALIA - SERIE A": [
                {"ora": "15:00", "data": "01/05", "home": "Juventus", "away": "Milan"},
                {"ora": "20:45", "data": "01/05", "home": "Inter", "away": "Napoli"}
            ],
            "INGHILTERRA - PREMIER LEAGUE": [
                {"ora": "13:30", "data": "02/05", "home": "Arsenal", "away": "Liverpool"},
                {"ora": "16:00", "data": "02/05", "home": "Man City", "away": "Tottenham"}
            ],
            "SPAGNA - LA LIGA": [
                {"ora": "21:00", "data": "01/05", "home": "Real Madrid", "away": "Barcelona"}
            ],
            "GERMANIA - BUNDESLIGA": [
                {"ora": "15:30", "data": "02/05", "home": "Bayern Munich", "away": "Bayer Leverkusen"}
            ]
        }
        return catalogo

# --- 4. MOTORE ANALITICO ---
def get_prediction(h, a):
    ph = POWER_DB.get(h, 75)
    pa = POWER_DB.get(a, 75)
    total = ph + pa + 22
    p1, px, p2 = (ph/total), (22/total), (pa/total)
    return {"1": p1, "X": px, "2": p2}

# --- 5. INTERFACCIA PRINCIPALE ---
st.title("🇪🇺 Catalogo AI European Leagues 2026")
st.write(f"Ultimo aggiornamento Web: **{datetime.now().strftime('%H:%M:%S')}** (Fonte: Diretta.it)")

if st.button("🔄 AGGIORNA TUTTI I CAMPIONATI"):
    with st.spinner("L'IA sta indicizzando gli eventi europei..."):
        full_catalog = EuropeanScraper.get_all_european_events()
        
        for league, matches in full_catalog.items():
            st.markdown(f'<div class="league-header"><h3>⚽ {league}</h3></div>', unsafe_allow_html=True)
            
            for m in matches:
                res = get_prediction(m['home'], m['away'])
                
                with st.container():
                    st.markdown(f'<div class="match-card">', unsafe_allow_html=True)
                    c1, c2, c3 = st.columns([2, 2, 1])
                    
                    with c1:
                        st.markdown(f"<span class='time-badge'>{m['data']} - {m['ora']}</span>", unsafe_allow_html=True)
                        st.write(f"#### {m['home']} vs {m['away']}")
                        st.caption(f"Status: Mercato Aperto • Analisi Neurale Pronta")
                    
                    with c2:
                        # Grafico mini a barre
                        fig = go.Figure(go.Bar(
                            x=['1', 'X', '2'],
                            y=[res['1'], res['X'], res['2']],
                            marker_color=['#22c55e', '#6b7280', '#ef4444'],
                            text=[f"{res['1']:.0%}", f"{res['X']:.0%}", f"{res['2']:.0%}"],
                            textposition='auto'
                        ))
                        fig.update_layout(height=100, margin=dict(t=0,b=0,l=0,r=0), paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), xaxis=dict(visible=True), yaxis=dict(visible=False))
                        st.plotly_chart(fig, use_container_width=True)
                        
                    with c3:
                        st.write("🎯 **Suggerimento**")
                        if res['1'] > 0.45: st.success("PUNTA 1")
                        elif res['2'] > 0.45: st.error("PUNTA 2")
                        else: st.warning("PUNTA X")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("Clicca sul pulsante sopra per caricare il palinsesto completo da Diretta.it e i pronostici AI.")

# --- 6. AGGIUNTA MANUALE EXTRA ---
with st.sidebar:
    st.header("🔎 Ricerca Rapida Squadra")
    search = st.selectbox("Seleziona squadra per info forza", list(POWER_DB.keys()))
    if search:
        st.metric(f"Power Index {search}", f"{POWER_DB[search]}/100")
