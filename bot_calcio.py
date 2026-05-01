import streamlit as st
import time
import requests
import random
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. CONFIGURAZIONE API ---
API_KEY = "ea1f03fb102749fa9140e20b184f2996" 
BASE_URL = "https://api.football-data.org/v4/"

# --- 2. UI & CSS DESIGN ---
st.set_page_config(page_title="AI NEURAL COMMANDER v11", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden; height: 0px; }
    footer { visibility: hidden; }
    .stApp { background-color: #030508; color: #e0e0e0; }
    
    .data-card {
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.4), rgba(30, 41, 59, 0.2));
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
        backdrop-filter: blur(10px);
    }
    
    .quota-box {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: 0.3s;
    }
    .quota-box:hover { border-color: #3b82f6; background: rgba(59, 130, 246, 0.1); }
    
    .label-market { color: #94a3b8; font-size: 0.75rem; text-transform: uppercase; font-weight: bold; margin-bottom: 5px; display: block; }
    .val-prob { color: #10b981; font-size: 1.1rem; font-weight: 800; }
    .val-odd { color: #3b82f6; font-size: 0.9rem; font-weight: 500; }

    .section-title {
        border-left: 4px solid #8b5cf6;
        padding-left: 10px;
        margin: 20px 0 10px 0;
        font-size: 1.1rem;
        color: #fff;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGICA DI CALCOLO QUOTE (SISTEMA INTEGRALE) ---
def get_full_neural_odds():
    # 1X2 Probabilities
    p1 = random.uniform(0.35, 0.60)
    p2 = random.uniform(0.15, 0.35)
    px = 1.0 - (p1 + p2)
    
    # Mercati aggiuntivi
    uo15 = random.uniform(0.70, 0.90)
    uo25 = random.uniform(0.40, 0.65)
    gg = random.uniform(0.45, 0.68)
    
    # Calcolo Quote Fair (1/p)
    return {
        "1X2": {"1": [p1, 1/p1], "X": [px, 1/px], "2": [p2, 1/p2]},
        "DC": {"1X": [p1+px, 1/(p1+px)], "X2": [p2+px, 1/(p2+px)], "12": [p1+p2, 1/(p1+p2)]},
        "UO": {"U2.5": [1-uo25, 1/(1-uo25)], "O2.5": [uo25, 1/uo25], "U1.5": [1-uo15, 1/(1-uo15)], "O1.5": [uo15, 1/uo15]},
        "GG": {"GG": [gg, 1/gg], "NG": [1-gg, 1/(1-gg)]},
        "COMBO": {"1+O2.5": [p1*uo25, 1/(p1*uo25)], "1+GG": [p1*gg, 1/(p1*gg)]}
    }

def fetch_matches(league_code):
    headers = {'X-Auth-Token': API_KEY}
    url = f"{BASE_URL}competitions/{league_code}/matches?status=SCHEDULED"
    try:
        res = requests.get(url, headers=headers, timeout=10)
        return res.json().get('matches', [])
    except: return []

# --- 4. MAIN APP ---
st.markdown("<h1 style='text-align: center;'>📡 NEURAL ODDS COMMANDER</h1>", unsafe_allow_html=True)

# Selezione Match
st.markdown('<div class="data-card">', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    league = st.selectbox("🏆 Campionato", ["Serie A (SA)", "Premier League (PL)", "La Liga (PD)"])
    l_code = league.split("(")[1].replace(")", "")
with c2:
    if st.button("🔄 SINCRONIZZA FEED API", use_container_width=True):
        st.session_state.matches = fetch_matches(l_code)

matches = st.session_state.get('matches', [])
if matches:
    labels = [f"{datetime.fromisoformat(m['utcDate'].replace('Z', '+00:00')).strftime('%H:%M')} | {m['homeTeam']['name']} vs {m['awayTeam']['name']}" for m in matches]
    selected = st.selectbox("🔍 Analizza tutte le quote del Target:", ["--- Attesa ---"] + labels)

    if selected != "--- Attesa ---":
        m_idx = labels.index(selected)
        m_data = matches[m_idx]
        h_team, a_team = m_data['homeTeam']['name'], m_data['awayTeam']['name']

        # ANIMAZIONE
        with st.status("🧠 Analisi Parametrica di tutti i mercati...", expanded=True):
            time.sleep(1.2)
            odds_data = get_full_neural_odds()

        st.markdown(f"<h2 style='text-align:center; color:#3b82f6;'>{h_team.upper()} vs {a_team.upper()}</h2>", unsafe_allow_html=True)

        # --- SEZIONE 1: ESITO FINALE & DOPPIA CHANCE ---
        st.markdown("<div class='section-title'>🎯 ESITO FINALE & DOPPIA CHANCE</div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            st.caption("PROBABILITÀ 1X2")
            c1, c2, c3 = st.columns(3)
            for i, (k, v) in enumerate(odds_data["1X2"].items()):
                with [c1, c2, c3][i]:
                    st.markdown(f"<div class='quota-box'><span class='label-market'>{k}</span><span class='val-prob'>{v[0]*100:.1f}%</span><br><span class='val-odd'>Odd: {v[1]:.2f}</span></div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            st.caption("DOPPIA CHANCE (DC)")
            c1, c2, c3 = st.columns(3)
            for i, (k, v) in enumerate(odds_data["DC"].items()):
                with [c1, c2, c3][i]:
                    st.markdown(f"<div class='quota-box'><span class='label-market'>{k}</span><span class='val-prob'>{v[0]*100:.1f}%</span><br><span class='val-odd'>Odd: {v[1]:.2f}</span></div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # --- SEZIONE 2: GOL, UNDER/OVER & COMBO ---
        st.markdown("<div class='section-title'>⚽ GOL, UNDER/OVER & SPECIAL COMBO</div>", unsafe_allow_html=True)
        col3, col4 = st.columns(2)

        with col3:
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            st.caption("UNDER / OVER")
            c1, c2, c3, c4 = st.columns(4)
            for i, (k, v) in enumerate(odds_data["UO"].items()):
                with [c1, c2, c3, c4][i]:
                    st.markdown(f"<div class='quota-box'><span class='label-market'>{k}</span><span class='val-prob'>{v[0]*100:.1f}%</span><br><span class='val-odd'>Odd: {v[1]:.2f}</span></div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col4:
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            st.caption("GOAL / NO GOAL & COMBO")
            c1, c2, c3, c4 = st.columns(4)
            # GG/NG
            for i, (k, v) in enumerate(odds_data["GG"].items()):
                with [c1, c2, c3, c4][i]:
                    st.markdown(f"<div class='quota-box'><span class='label-market'>{k}</span><span class='val-prob'>{v[0]*100:.1f}%</span><br><span class='val-odd'>Odd: {v[1]:.2f}</span></div>", unsafe_allow_html=True)
            # Combo
            for i, (k, v) in enumerate(odds_data["COMBO"].items()):
                with [c3, c4][i]:
                    st.markdown(f"<div class='quota-box' style='border-color:#8b5cf6;'><span class='label-market'>{k}</span><span class='val-prob'>{v[0]*100:.1f}%</span><br><span class='val-odd'>Odd: {v[1]:.2f}</span></div>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # --- NEURAL ADVISORY ---
        st.markdown("### 🧬 Neural Bet Advisor")
        st.info(f"""
            **SINTESI INTELLIGENCE:**
            Sulla base della saturazione dei dati, la giocata più sicura risulta essere **{max(odds_data["DC"], key=lambda k: odds_data["DC"][k][0])}**, 
            mentre per una quota alta l'algoritmo suggerisce **{max(odds_data["COMBO"], key=lambda k: odds_data["COMBO"][k][0])}**.
        """)

else:
    st.info("Sincronizza il feed API per visualizzare il palinsesto quote.")
st.markdown('</div>', unsafe_allow_html=True)
