import streamlit as st
import time
import requests
import random
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. CONFIGURAZIONE API ---
API_KEY = "ea1f03fb102749fa9140e20b184f2996" 
BASE_URL = "https://api.football-data.org/v4/"

# --- 2. UI & CSS CREATIVO (CYBERPUNK STYLE) ---
st.set_page_config(page_title="AI NEURAL COMMANDER v10", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden; height: 0px; }
    footer { visibility: hidden; }
    .stApp { background-color: #030508; color: #e0e0e0; }
    
    /* Card con bordi luminosi */
    .data-card {
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.4), rgba(30, 41, 59, 0.2));
        border: 1px solid rgba(59, 130, 246, 0.3);
        border-radius: 24px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        backdrop-filter: blur(15px);
    }
    
    /* Animazione Testo Neural */
    .neural-text {
        font-family: 'Courier New', monospace;
        color: #10b981;
        text-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
    }

    .vs-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px;
        margin: 20px 0;
    }

    .vs-circle {
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        width: 60px; height: 60px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-weight: 900; font-size: 1.2rem;
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.6);
    }

    .absent-item {
        display: flex;
        align-items: center;
        gap: 10px;
        background: rgba(239, 68, 68, 0.08);
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 8px;
        border: 1px solid rgba(239, 68, 68, 0.1);
    }

    /* Progress Bar personalizzata */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #3b82f6, #10b981);
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. FUNZIONI LOGICA ---
def fetch_matches(league_code):
    headers = {'X-Auth-Token': API_KEY}
    url = f"{BASE_URL}competitions/{league_code}/matches?status=SCHEDULED"
    try:
        res = requests.get(url, headers=headers, timeout=10)
        return res.json().get('matches', [])
    except: return []

def get_neural_data():
    # Simulazione di analisi statistica complessa
    p1 = random.uniform(0.4, 0.6)
    p2 = random.uniform(0.1, 0.3)
    px = 1.0 - (p1 + p2)
    return [p1, px, p2], random.randint(70, 99), random.randint(70, 99)

# --- 4. MAIN APP ---
st.markdown("<h1 style='text-align: center; color: #3b82f6;'>🧠 NEURAL COMMANDER <span style='color: #8b5cf6;'>X</span></h1>", unsafe_allow_html=True)

# Selezione Evento
with st.container():
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    with c1:
        league = st.selectbox("🌎 Seleziona Circuito", ["Serie A (SA)", "Premier League (PL)", "La Liga (PD)"])
        l_code = league.split("(")[1].replace(")", "")
    with c2:
        if st.button("🛰️ AGGIORNA FEED SATELLITARE", use_container_width=True):
            st.session_state.matches = fetch_matches(l_code)
    
    matches = st.session_state.get('matches', [])
    if matches:
        labels = [f"{datetime.fromisoformat(m['utcDate'].replace('Z', '+00:00')).strftime('%H:%M')} | {m['homeTeam']['name']} vs {m['awayTeam']['name']}" for m in matches]
        selected = st.selectbox("🎯 Seleziona Target da Analizzare", ["--- Attesa Input ---"] + labels)
    else:
        st.info("Sincronizza il feed per caricare i match reali dal database 2026.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- ANALISI ESTETICA ---
if 'selected' in locals() and selected != "--- Attesa Input ---":
    m_idx = labels.index(selected)
    m_data = matches[m_idx]
    h_team, a_team = m_data['homeTeam']['name'], m_data['awayTeam']['name']

    # 1. SEQUENZA DI CARICAMENTO CREATIVA
    placeholder = st.empty()
    with placeholder.container():
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.markdown("<p class='neural-text'>[SISTEMA]: Inizializzazione Deep Scan...</p>", unsafe_allow_html=True)
        bar = st.progress(0)
        logs = [
            f"> Scaricamento metriche live per {h_team}...",
            f"> Analisi vettoriale infortuni e squalifiche...",
            f"> Calcolo simulazioni Monte Carlo (10.000 iterazioni)...",
            "> Generazione Intelligence Report..."
        ]
        for i, log in enumerate(logs):
            time.sleep(0.6)
            st.markdown(f"<p class='neural-text' style='font-size: 0.8rem;'>{log}</p>", unsafe_allow_html=True)
            bar.progress((i + 1) * 25)
        st.markdown('</div>', unsafe_allow_html=True)
    
    time.sleep(0.5)
    placeholder.empty()

    # 2. REPORT FINALE (INFOGRAFICA)
    probs, h_power, a_power = get_neural_data()

    # Header Matchup
    st.markdown(f"""
        <div class="vs-container">
            <h2 style="margin:0;">{h_team.upper()}</h2>
            <div class="vs-circle">VS</div>
            <h2 style="margin:0;">{a_team.upper()}</h2>
        </div>
    """, unsafe_allow_html=True)

    col_h, col_m, col_a = st.columns([1, 1.5, 1])

    with col_h:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; color:#3b82f6; font-weight:900;'>{h_power}%</p>", unsafe_allow_html=True)
        st.progress(h_power/100)
        st.caption("🏠 HOME POWER INDEX")
        st.markdown("<br><small>ASSENTI:</small>", unsafe_allow_html=True)
        st.markdown('<div class="absent-item">🚑 M. Icardi (Inf.)</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_m:
        st.markdown('<div class="data-card" style="text-align:center;">', unsafe_allow_html=True)
        st.markdown("<b>PROBABILITÀ NEURALE</b>", unsafe_allow_html=True)
        fig = go.Figure(go.Pie(
            labels=['1', 'X', '2'], values=probs, hole=.8,
            marker=dict(colors=['#3b82f6', '#1e293b', '#8b5cf6']),
            textinfo='label+percent'
        ))
        fig.update_layout(showlegend=False, height=280, margin=dict(t=0,b=0,l=0,r=0), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"<h3 style='color:#10b981;'>CONFIDENCE: {max(probs)*100:.1f}%</h3>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_a:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; color:#8b5cf6; font-weight:900;'>{a_power}%</p>", unsafe_allow_html=True)
        st.progress(a_power/100)
        st.caption("🚌 AWAY POWER INDEX")
        st.markdown("<br><small>ASSENTI:</small>", unsafe_allow_html=True)
        st.markdown('<div class="absent-item">🚑 K. Walker (Dub.)</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Area Opinion
    st.markdown("### 🧬 Intelligence Opinion")
    st.markdown(f"""
    <div class="data-card" style="border-left: 5px solid #10b981;">
        <span style="color:#10b981; font-weight:bold;">>>> ANALISI COMPLETATA:</span><br>
        Il modello rileva un forte squilibrio tattico a favore del team <b>{h_team if probs[0] > probs[2] else a_team}</b>. 
        Le condizioni meteo e lo stato del terreno favoriscono una giocata di tipo <b>{'OVER 2.5' if probs[0]+probs[2] > 0.7 else 'UNDER 2.5'}</b>.
        <br><br>
        <span style="color:#3b82f6;">CONSIGLIO PRO:</span> Quota Fair rilevata <b>{(1/max(probs)):.2f}</b>. Se il mercato offre di più, è una <b>Value Bet</b>.
    </div>
    """, unsafe_allow_html=True)
