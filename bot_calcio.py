import streamlit as st
import time
import requests
import random
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. CONFIGURAZIONE API ---
API_KEY = "LA_TUA_API_KEY" 
BASE_URL = "https://api.football-data.org/v4/"

# --- 2. UI & CSS AVANZATO ---
st.set_page_config(page_title="AI NEURAL COMMANDER PRO", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden; height: 0px; }
    footer { visibility: hidden; }
    .stApp { background-color: #05070a; color: #e0e0e0; }
    
    .data-card {
        background: rgba(30, 41, 59, 0.25);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
        backdrop-filter: blur(10px);
    }
    
    .neural-box {
        background: rgba(16, 185, 129, 0.05);
        border-left: 4px solid #10b981;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
        font-family: 'Courier New', monospace;
        font-size: 0.85rem;
    }

    .absent-card {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.2);
        padding: 10px;
        border-radius: 10px;
        margin-top: 5px;
    }

    .player-name { color: #ef4444; font-weight: bold; }
    .player-reason { color: #94a3b8; font-size: 0.8rem; }
    
    .status-badge {
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: bold;
        text-transform: uppercase;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGICA DI GENERAZIONE DETTAGLI (SIMULAZIONE INTELLIGENTE) ---
def get_match_details(h_name, a_name):
    # Simulazione database infortunati/assenti per il 2026
    reasons = ["Infortunio Muscolare", "Rottura Legamenti", "Squalifica (Somma ammonizioni)", "Problema Fisico (Dubbio)", "Squalifica (Rosso diretto)"]
    
    def generate_players(team):
        players = ["M. Rossi", "J. Doe", "L. Martinez", "K. Benzema", "G. Silva", "A. Muller", "P. Pogba", "V. Junior"]
        num = random.randint(0, 3)
        return [{"name": random.choice(players), "reason": random.choice(reasons)} for _ in range(num)]

    return {
        "home_absents": generate_players(h_name),
        "away_absents": generate_players(a_name),
        "referee": random.choice(["D. Orsato", "M. Oliver", "S. Marciniak", "C. Turpin"]),
        "weather": random.choice(["Sereno (22°C)", "Pioggia Leggera (14°C)", "Nuvoloso (18°C)", "Umidità Elevata (26°C)"]),
        "stadium_fill": random.randint(85, 100),
        "tactical_focus": random.choice([
            "Focus su transizioni rapide e contropiede.",
            "Possesso palla prolungato e costruzione dal basso.",
            "Difesa a blocco basso e ripartenze fulminee.",
            "Pressione alta costante per indurre all'errore."
        ])
    }

def get_neural_probs():
    p1, px, p2 = random.uniform(0.4, 0.6), random.uniform(0.2, 0.3), random.uniform(0.1, 0.3)
    t = p1 + px + p2
    return [p1/t, px/t, p2/t]

def fetch_matches(league_code):
    headers = {'X-Auth-Token': API_KEY}
    url = f"{BASE_URL}competitions/{league_code}/matches?status=SCHEDULED"
    try:
        res = requests.get(url, headers=headers, timeout=10)
        return res.json().get('matches', [])
    except: return []

# --- 4. MAIN APP ---
st.title("🛡️ AI NEURAL COMMANDER v9.5")

# Selettore Campionato
st.markdown('<div class="data-card">', unsafe_allow_html=True)
c1, c2 = st.columns([1, 2])
with c1:
    league = st.selectbox("🏆 Campionato", ["Serie A (SA)", "Premier League (PL)", "La Liga (PD)"])
    l_code = league.split("(")[1].replace(")", "")
with c2:
    if st.button("🔄 SINCRONIZZA CALENDARIO LIVE", use_container_width=True):
        st.session_state.matches = fetch_matches(l_code)

matches = st.session_state.get('matches', [])

if matches:
    labels = [f"{datetime.fromisoformat(m['utcDate'].replace('Z', '+00:00')).strftime('%H:%M')} | {m['homeTeam']['name']} vs {m['awayTeam']['name']}" for m in matches]
    selected = st.selectbox("🔍 Seleziona Match per Report Dettagliato:", ["--- Seleziona ---"] + labels)

    if selected != "--- Seleziona ---":
        m_idx = labels.index(selected)
        m_data = matches[m_idx]
        h_name, a_name = m_data['homeTeam']['name'], m_data['awayTeam']['name']
        
        with st.status("🧬 Deep Scanning Evento in corso...", expanded=True) as s:
            time.sleep(0.8)
            details = get_match_details(h_name, a_name)
            probs = get_neural_probs()
            s.update(label="Analisi Giocatori e Tattica Completata!", state="complete")

        # --- LAYOUT REPORT ---
        st.markdown(f"<div style='text-align:center;'><h2>{h_name.upper()} vs {a_name.upper()}</h2></div>", unsafe_allow_html=True)
        
        col_stats, col_details = st.columns([1.5, 1])

        with col_stats:
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            st.subheader("📊 Analisi Probabilistica")
            c1, c2, c3 = st.columns(3)
            c1.metric("1", f"{probs[0]*100:.1f}%")
            c2.metric("X", f"{probs[1]*100:.1f}%")
            c3.metric("2", f"{probs[2]*100:.1f}%")
            
            st.markdown(f"""
            <div class="neural-box">
                <b>🤖 FOCUS TATTICO:</b><br>{details['tactical_focus']}<br><br>
                <b>📢 CLIMA MATCH:</b> {details['weather']}<br>
                <b>🏟️ RIEMPIMENTO STADIO:</b> {details['stadium_fill']}%<br>
                <b>⚖️ ARBITRO:</b> {details['referee']}
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_details:
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            st.subheader("🚑 Bollettino Assenti")
            
            # Assenti Casa
            st.write(f"**{h_name}**")
            if not details['home_absents']: st.write("✅ Rosa completa")
            for p in details['home_absents']:
                st.markdown(f"""<div class='absent-card'><span class='player-name'>{p['name']}</span><br><span class='player-reason'>{p['reason']}</span></div>""", unsafe_allow_html=True)
            
            st.write("")
            # Assenti Trasferta
            st.write(f"**{a_name}**")
            if not details['away_absents']: st.write("✅ Rosa completa")
            for p in details['away_absents']:
                st.markdown(f"""<div class='absent-card'><span class='player-name'>{p['name']}</span><br><span class='player-reason'>{p['reason']}</span></div>""", unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("Sincronizza per visualizzare i match programmati.")
st.markdown('</div>', unsafe_allow_html=True)
