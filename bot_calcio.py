import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. DATABASE SQUADRE (Power Index) ---
TEAMS_DB = {
    "Inter": 90, "Milan": 84, "Juventus": 83, "Napoli": 81, "Atalanta": 82,
    "Roma": 78, "Lazio": 77, "Bologna": 76, "Fiorentina": 75, "Torino": 73,
    "Real Madrid": 96, "Man City": 95, "Liverpool": 93, "Arsenal": 92, "Bayern Munich": 90
}

# --- 2. PALINSESTO PARTITE (Calendario Programmato) ---
# Qui inserisci le partite in programma. L'IA le caricherà in automatico.
SCHEDULED_MATCHES = [
    {"data": "2026-05-02", "lega": "Serie A", "home": "Inter", "away": "Milan"},
    {"data": "2026-05-02", "lega": "Serie A", "home": "Juventus", "away": "Napoli"},
    {"data": "2026-05-03", "lega": "Champions League", "home": "Real Madrid", "away": "Man City"},
    {"data": "2026-05-03", "lega": "Serie A", "home": "Roma", "away": "Lazio"},
    {"data": "2026-05-04", "lega": "Premier League", "home": "Liverpool", "away": "Arsenal"}
]

# --- 3. CONFIGURAZIONE PAGINA E CSS ---
st.set_page_config(page_title="AI CALENDAR PREDICTOR", layout="wide")

st.markdown("""
    <style>
    #MainMenu, header, footer {visibility: hidden; display: none !important;}
    .stApp { background: #0e1117; }
    .match-card { 
        background: #161b22; border-radius: 15px; padding: 20px; 
        border: 1px solid #30363d; margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. MOTORE DI CALCOLO ---
def get_prediction(home, away):
    ph = TEAMS_DB.get(home, 50)
    pa = TEAMS_DB.get(away, 50)
    
    # Calcolo probabilistico con vantaggio casa
    score_h = ph + 6 
    score_a = pa
    total = score_h + score_a
    
    p1 = (score_h / total) * 1.05
    p2 = (score_a / total) * 0.95
    px = 1.0 - (p1 + p2)
    
    # Normalizzazione
    if px < 0.22: px = 0.25
    norm = p1 + px + p2
    return {"1": p1/norm, "X": px/norm, "2": p2/norm}

# --- 5. INTERFACCIA ---
st.title("📅 AI Sport Planner 2026")
st.write("Analisi automatica delle partite in programma nel database interno.")

# Sidebar per filtri
with st.sidebar:
    st.header("Filtra Palinsesto")
    date_filter = st.date_input("Seleziona Data", datetime.strptime("2026-05-02", "%Y-%m-%d"))
    date_str = date_filter.strftime("%Y-%m-%d")

# Filtriamo i match in base alla data scelta
matches_today = [m for m in SCHEDULED_MATCHES if m['data'] == date_str]

if not matches_today:
    st.info(f"Nessuna partita in programma per il {date_str}. Prova il 2026-05-02 o 2026-05-03.")
else:
    st.subheader(f"Partite del {date_str}")
    
    for match in matches_today:
        res = get_prediction(match['home'], match['away'])
        
        with st.container():
            st.markdown(f'''
            <div class="match-card">
                <span style="color: #888;">{match['lega']}</span>
                <h2 style="margin: 0;">{match['home']} vs {match['away']}</h2>
            </div>
            ''', unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns([1, 2, 1])
            
            with c1:
                st.write("### 📈 Probabilità")
                st.write(f"**1**: {res['1']:.1%}")
                st.write(f"**X**: {res['X']:.1%}")
                st.write(f"**2**: {res['2']:.1%}")
            
            with c2:
                # Grafico rapido
                fig = go.Figure(go.Bar(
                    x=['1', 'X', '2'],
                    y=[res['1'], res['X'], res['2']],
                    marker_color=['#22c55e', '#6b7280', '#ef4444']
                ))
                fig.update_layout(height=150, margin=dict(t=0,b=0,l=0,r=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
                st.plotly_chart(fig, use_container_width=True)
                
            with c3:
                st.write("### 🤖 Verdetto")
                if res['1'] > 0.55: st.success("Punta sull'1")
                elif res['2'] > 0.55: st.success("Punta sul 2")
                else: st.warning("Partita da X")
            st.divider()

# --- 6. AGGIUNTA MANUALE (Opzionale) ---
with st.expander("➕ Aggiungi una partita al volo"):
    col1, col2, col3 = st.columns(3)
    with col1: h_new = st.selectbox("Casa", list(TEAMS_DB.keys()), key="h")
    with col2: a_new = st.selectbox("Trasferta", list(TEAMS_DB.keys()), key="a")
    if st.button("Analizza Partita Extra"):
        r_extra = get_prediction(h_new, a_new)
        st.write(f"Risultato Analisi: **1**: {r_extra['1']:.1%} | **X**: {r_extra['X']:.1%} | **2**: {r_extra['2']:.1%}")
