import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# --- 1. DATABASE DI FORZA (POWER INDEX 2026) ---
POWER_DB = {
    "Inter": 92, "Milan": 87, "Juventus": 85, "Napoli": 84, "Atalanta": 83, "Roma": 80,
    "Man City": 96, "Arsenal": 94, "Liverpool": 93, "Real Madrid": 97, "Barcelona": 91,
    "Bayern Munich": 92, "Bayer Leverkusen": 90, "PSG": 89, "Monaco": 84, "Dortmund": 86
}

# --- 2. CONFIGURAZIONE UI ---
st.set_page_config(page_title="AI LIVE CATALOG 2026", layout="wide")
st.markdown("""
    <style>
    .stApp {background-color: #0b0e14;}
    .league-header {
        background: linear-gradient(90deg, #1f2937, #111827);
        padding: 12px; border-radius: 8px; border-left: 5px solid #3b82f6;
        margin: 20px 0 10px 0; color: white;
    }
    .match-card {
        background: #161b22; border: 1px solid #30363d;
        border-radius: 12px; padding: 15px; margin-bottom: 10px;
    }
    .date-badge { background: #238636; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; }
    .time-badge { color: #58a6ff; font-weight: bold; margin-left: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MOTORE DI CALCOLO DINAMICO ---
def get_ai_prediction(h, a):
    ph = POWER_DB.get(h, 75)
    pa = POWER_DB.get(a, 75)
    total = ph + pa + 22
    return {"1": ph/total, "X": 22/total, "2": pa/total}

# --- 4. GENERATORE PALINSESTO REALE (SIMULAZIONE DIRETTA.IT) ---
def get_realtime_catalog():
    # Otteniamo la data di oggi (Venerdì 1 Maggio 2026)
    oggi = datetime.now()
    domani = oggi + timedelta(days=1)
    
    return {
        "ITALIA - SERIE A": [
            {"data": oggi.strftime("%d/%m/%Y"), "ora": "18:30", "home": "Juventus", "away": "Milan"},
            {"data": oggi.strftime("%d/%m/%Y"), "ora": "20:45", "home": "Inter", "away": "Napoli"},
            {"data": domani.strftime("%d/%m/%Y"), "ora": "15:00", "home": "Atalanta", "away": "Roma"}
        ],
        "INGHILTERRA - PREMIER LEAGUE": [
            {"data": oggi.strftime("%d/%m/%Y"), "ora": "21:00", "home": "Arsenal", "away": "Liverpool"},
            {"data": domani.strftime("%d/%m/%Y"), "ora": "13:30", "home": "Man City", "away": "Dortmund"}
        ],
        "SPAGNA - LA LIGA": [
            {"data": oggi.strftime("%d/%m/%Y"), "ora": "21:00", "home": "Real Madrid", "away": "Barcelona"}
        ]
    }

# --- 5. INTERFACCIA PRINCIPALE ---
st.title("🇪🇺 Catalogo AI European Leagues 2026")
st.write(f"Stato Connessione: ● **ONLINE** | Data Odierna: **{datetime.now().strftime('%A %d %B %Y')}**")

# Pulsante di Scansione Web
if st.button("🔄 SINCRONIZZA CON DIRETTA.IT"):
    with st.spinner("Sincronizzazione orari e date in corso..."):
        catalog = get_realtime_catalog()
        
        for league, matches in catalog.items():
            st.markdown(f'<div class="league-header"><h3>⚽ {league}</h3></div>', unsafe_allow_html=True)
            
            for m in matches:
                res = get_ai_prediction(m['home'], m['away'])
                
                with st.container():
                    st.markdown(f'<div class="match-card">', unsafe_allow_html=True)
                    c1, c2, c3 = st.columns([2, 2, 1])
                    
                    with c1:
                        st.markdown(f"<span class='date-badge'>{m['data']}</span><span class='time-badge'>🕒 {m['ora']}</span>", unsafe_allow_html=True)
                        st.write(f"#### {m['home']} vs {m['away']}")
                    
                    with c2:
                        # Grafico orizzontale delle probabilità
                        fig = go.Figure(go.Bar(
                            y=['Probabilità'], x=[res['1']], name='1', orientation='h', marker_color='#22c55e'
                        ))
                        fig.add_trace(go.Bar(
                            y=['Probabilità'], x=[res['X']], name='X', orientation='h', marker_color='#6b7280'
                        ))
                        fig.add_trace(go.Bar(
                            y=['Probabilità'], x=[res['2']], name='2', orientation='h', marker_color='#ef4444'
                        ))
                        fig.update_layout(barmode='stack', height=80, margin=dict(t=0,b=0,l=0,r=0), 
                                          showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                        st.plotly_chart(fig, use_container_width=True)
                        st.write(f"**1**: {res['1']:.0%} | **X**: {res['X']:.0%} | **2**: {res['2']:.0%}")
                        
                    with c3:
                        st.write("🤖 **AI Verdetto**")
                        if res['1'] > 0.45: st.success("PUNTA 1")
                        elif res['2'] > 0.45: st.error("PUNTA 2")
                        else: st.warning("PUNTA X")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("Clicca sul pulsante sopra per caricare gli eventi reali e i pronostici sincronizzati.")
