import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. DATABASE COMPLETO SQUADRE (Power Index Europeo) ---
TEAMS_DB = {
    "Italia - Serie A": {
        "Inter": 91, "Milan": 85, "Juventus": 84, "Napoli": 82, "Atalanta": 83, 
        "Roma": 79, "Lazio": 78, "Fiorentina": 77, "Bologna": 78, "Torino": 74
    },
    "Inghilterra - Premier League": {
        "Man City": 96, "Arsenal": 93, "Liverpool": 94, "Aston Villa": 84, 
        "Tottenham": 83, "Man United": 81, "Newcastle": 82, "Chelsea": 80
    },
    "Spagna - La Liga": {
        "Real Madrid": 97, "Barcelona": 89, "Girona": 84, "Atletico Madrid": 86, 
        "Athletic Bilbao": 82, "Real Sociedad": 81, "Betis": 79
    },
    "Germania - Bundesliga": {
        "Bayer Leverkusen": 90, "Bayern Munich": 91, "Stuttgart": 84, 
        "RB Leipzig": 85, "Borussia Dortmund": 86, "Eintracht Frankfurt": 80
    },
    "Francia - Ligue 1": {
        "PSG": 88, "Monaco": 82, "Brest": 79, "Lille": 81, "Nice": 78, "Lyon": 77
    }
}

# --- 2. CATALOGO PARTITE IN PROGRAMMA (Palinsesto) ---
# Aggiungi qui le partite per ogni weekend
EUROPEAN_SCHEDULE = [
    {"data": "2026-05-02", "campionato": "Italia - Serie A", "home": "Inter", "away": "Milan"},
    {"data": "2026-05-02", "campionato": "Inghilterra - Premier League", "home": "Arsenal", "away": "Liverpool"},
    {"data": "2026-05-03", "campionato": "Spagna - La Liga", "home": "Real Madrid", "away": "Barcelona"},
    {"data": "2026-05-03", "campionato": "Germania - Bundesliga", "home": "Bayern Munich", "away": "Bayer Leverkusen"},
    {"data": "2026-05-04", "campionato": "Francia - Ligue 1", "home": "PSG", "away": "Monaco"},
]

# --- 3. CONFIGURAZIONE E STILE ---
st.set_page_config(page_title="AI EUROPEAN CATALOG", layout="wide")

st.markdown("""
    <style>
    #MainMenu, header, footer {visibility: hidden; display: none !important;}
    .stApp { background: #0b0e14; }
    .league-header {
        background: linear-gradient(90deg, #1f2937, #111827);
        padding: 10px 20px; border-radius: 10px; border-left: 5px solid #3b82f6; margin-bottom: 20px;
    }
    .match-box {
        background: #161b22; border: 1px solid #30363d;
        border-radius: 12px; padding: 20px; margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. MOTORE ANALITICO ---
def analyze_match(home, away, campionato):
    db = TEAMS_DB.get(campionato, {})
    ph = db.get(home, 70)
    pa = db.get(away, 70)
    
    # Calcolo pesato (Fattore campo +10%)
    score_h = ph * 1.10
    score_a = pa
    total = score_h + score_a
    
    p1 = score_h / total
    p2 = score_a / total
    px = 0.26  # Pareggio base statistico europeo
    
    # Normalizzazione per somma 1.0
    sum_p = p1 + p2 + px
    return {"1": p1/sum_p, "X": px/sum_p, "2": p2/sum_p}

# --- 5. INTERFACCIA ---
st.title("🇪🇺 Catalogo AI Pronostici Europei 2026")

# Filtri Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/football.png", width=80)
    st.header("Filtra Catalogo")
    selected_date = st.date_input("Data Eventi", datetime.strptime("2026-05-02", "%Y-%m-%d"))
    date_str = selected_date.strftime("%Y-%m-%d")
    
    selected_league = st.multiselect(
        "Seleziona Campionati", 
        list(TEAMS_DB.keys()), 
        default=list(TEAMS_DB.keys())
    )

# Visualizzazione Palinsesto
matches_filtered = [
    m for m in EUROPEAN_SCHEDULE 
    if m['data'] == date_str and m['campionato'] in selected_league
]

if not matches_filtered:
    st.info(f"Nessun evento a catalogo per il {date_str} nei campionati selezionati.")
else:
    # Raggruppiamo per campionato per ordine visivo
    current_league = ""
    for match in matches_filtered:
        if match['campionato'] != current_league:
            current_league = match['campionato']
            st.markdown(f'<div class="league-header"><h3>⚽ {current_league}</h3></div>', unsafe_allow_html=True)
        
        res = analyze_match(match['home'], match['away'], match['campionato'])
        
        with st.container():
            st.markdown(f'<div class="match-box">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.write(f"#### {match['home']} vs {match['away']}")
                st.write(f"⏱️ Data: {match['data']}")
                st.write(f"📊 **Power Index:** {TEAMS_DB[match['campionato']][match['home']]} vs {TEAMS_DB[match['campionato']][match['away']]}")
            
            with col2:
                # Grafico delle percentuali
                fig = go.Figure(go.Bar(
                    x=['1', 'X', '2'],
                    y=[res['1'], res['X'], res['2']],
                    marker_color=['#22c55e', '#94a3b8', '#ef4444'],
                    text=[f"{res['1']:.0%}", f"{res['X']:.0%}", f"{res['2']:.0%}"],
                    textposition='auto',
                ))
                fig.update_layout(height=120, margin=dict(t=0,b=0,l=0,r=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), xaxis=dict(visible=True), yaxis=dict(visible=False))
                st.plotly_chart(fig, use_container_width=True)
                
            with col3:
                st.write("### AI Verdetto")
                prob_max = max(res.values())
                if res['1'] == prob_max: st.success("🎯 SEGNO: 1")
                elif res['2'] == prob_max: st.error("🎯 SEGNO: 2")
                else: st.warning("🎯 SEGNO: X")
            
            st.markdown('</div>', unsafe_allow_html=True)
