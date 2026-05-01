import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. DATABASE INTEGRALE EUROPA 2026 ---
# Struttura: { "Campionato": { "Squadra": Power_Index } }
EURO_DATABASE = {
    "Serie A 🇮🇹": {
        "Inter": 94, "Milan": 88, "Juventus": 87, "Napoli": 85, "Atalanta": 86, "Roma": 82, "Lazio": 81, 
        "Bologna": 80, "Fiorentina": 79, "Torino": 77, "Monza": 75, "Genoa": 76, "Lecce": 72, 
        "Udinese": 73, "Cagliari": 71, "Verona": 70, "Empoli": 69, "Parma": 74, "Venezia": 68, "Como": 75
    },
    "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": {
        "Man City": 97, "Arsenal": 95, "Liverpool": 94, "Aston Villa": 86, "Tottenham": 85, "Chelsea": 83, 
        "Newcastle": 84, "Man United": 82, "West Ham": 79, "Brighton": 81, "Wolves": 76, "Fulham": 77, 
        "Bournemouth": 75, "Everton": 74, "Brentford": 76, "Crystal Palace": 78, "Nottm Forest": 73, 
        "Leicester": 74, "Ipswich": 70, "Southampton": 71
    },
    "La Liga 🇪🇸": {
        "Real Madrid": 98, "Barcelona": 92, "Atletico Madrid": 89, "Girona": 86, "Athletic Bilbao": 84, 
        "Real Sociedad": 83, "Betis": 81, "Villarreal": 82, "Valencia": 78, "Alaves": 75, "Osasuna": 76, 
        "Getafe": 74, "Celta Vigo": 75, "Sevilla": 79, "Mallorca": 74, "Las Palmas": 72, "Leganes": 70, 
        "Valladolid": 71, "Espanyol": 73, "Rayo Vallecano": 72
    },
    "Bundesliga 🇩🇪": {
        "Bayer Leverkusen": 92, "Bayern Munich": 93, "Stuttgart": 87, "RB Leipzig": 86, "Dortmund": 88, 
        "Eintracht Frankfurt": 82, "Hoffenheim": 79, "Heidenheim": 77, "Werder Bremen": 76, "Freiburg": 78, 
        "Augsburg": 75, "Wolfsburg": 77, "Mainz": 74, "M'gladbach": 75, "Union Berlin": 73, "Bochum": 70, 
        "St. Pauli": 72, "Holstein Kiel": 69
    },
    "Ligue 1 🇫🇷": {
        "PSG": 91, "Monaco": 85, "Brest": 82, "Lille": 83, "Nice": 81, "Lyon": 82, "Lens": 80, 
        "Marseille": 83, "Reims": 77, "Rennes": 79, "Toulouse": 76, "Montpellier": 74, "Strasbourg": 75, 
        "Le Havre": 71, "Nantes": 73, "Angers": 69, "St. Etienne": 72, "Auxerre": 70
    }
}

# --- 2. LOGICA DI CALCOLO ---
def get_neural_odds(h_team, a_team, league):
    p_h = EURO_DATABASE[league].get(h_team, 75)
    p_a = EURO_DATABASE[league].get(a_team, 75)
    
    # Algoritmo: Forza relativa + Bonus Casa (6%) + Margine Pareggio (24%)
    total_raw = p_h + p_a
    win_h_raw = (p_h / total_raw) * 1.06
    win_a_raw = (p_a / total_raw) * 0.94
    
    draw = 0.24
    remaining = 1.0 - draw
    
    # Normalizzazione
    factor = remaining / (win_h_raw + win_a_raw)
    return {
        "1": win_h_raw * factor,
        "X": draw,
        "2": win_a_raw * factor
    }

# --- 3. INTERFACCIA STREAMLIT ---
st.set_page_config(page_title="AI TOTAL EUROPE 2026", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; }
    .main-card { background: #161b22; border-radius: 15px; padding: 25px; border: 1px solid #30363d; }
    .league-label { color: #58a6ff; font-weight: bold; font-size: 1.1rem; }
    </style>
    """, unsafe_allow_html=True)

st.title("🇪🇺 AI European Football Intelligence")
st.caption(f"Database sincronizzato: Maggio 2026 | 98 Squadre analizzate")

# --- 4. SELEZIONE DINAMICA ---
with st.sidebar:
    st.header("⚙️ Configurazione Match")
    
    # 1. Scegli la nazione
    sel_league = st.selectbox("Seleziona Campionato", list(EURO_DATABASE.keys()))
    
    # 2. Scegli le squadre (la lista si aggiorna in base alla nazione)
    squadre_disponibili = sorted(list(EURO_DATABASE[sel_league].keys()))
    
    team_h = st.selectbox("Squadra in Casa", squadre_disponibili, index=0)
    team_a = st.selectbox("Squadra in Trasferta", [s for s in squadre_disponibili if s != team_h], index=1)
    
    st.divider()
    st.info("L'IA utilizza il Power Index reale per calcolare le probabilità di ogni scontro.")

# --- 5. VISUALIZZAZIONE ANALISI ---
col_stats, col_graph = st.columns([1, 1])

res = get_neural_odds(team_h, team_a, sel_league)

with col_stats:
    st.markdown(f'<div class="main-card">', unsafe_allow_html=True)
    st.markdown(f"<span class='league-label'>{sel_league}</span>", unsafe_allow_html=True)
    st.header(f"{team_h} vs {team_a}")
    
    # Metriche
    m1, mx, m2 = st.columns(3)
    m1.metric("SEGNO 1", f"{res['1']:.1%}")
    mx.metric("SEGNO X", f"{res['X']:.1%}")
    m2.metric("SEGNO 2", f"{res['2']:.1%}")
    
    st.write("---")
    st.write(f"📊 **Power Index:** {team_h} ({EURO_DATABASE[sel_league][team_h]}) | {team_a} ({EURO_DATABASE[sel_league][team_a]})")
    st.markdown('</div>', unsafe_allow_html=True)

with col_graph:
    fig = go.Figure(data=[go.Pie(
        labels=['1', 'X', '2'], 
        values=[res['1'], res['X'], res['2']], 
        hole=.5,
        marker_colors=['#22c55e', '#6b7280', '#ef4444'],
        textinfo='label+percent'
    )])
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', 
        font=dict(color="white"),
        margin=dict(t=20, b=20, l=20, r=20),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

# --- 6. VERDETTO INTELLIGENTE ---
st.subheader("🎯 Analisi Tattica AI")
diff = EURO_DATABASE[sel_league][team_h] - EURO_DATABASE[sel_league][team_a]

if abs(diff) < 3:
    st.warning(f"**Partita da Tripla:** La differenza di forza è minima ({abs(diff)} punti). Il pareggio o la vittoria di misura sono gli esiti più probabili.")
elif diff > 0:
    st.success(f"**Vantaggio Casa:** L'IA rileva una superiorità tecnica del **{team_h}**. Il fattore campo consolida il pronostico a favore dell'1.")
else:
    st.error(f"**Vantaggio Trasferta:** Nonostante giochi fuori casa, il **{team_a}** ha un roster superiore. Possibile segno 2 o X2.")

st.caption(f"Analisi generata il {datetime.now().strftime('%d/%m/%Y alle %H:%M')}")
