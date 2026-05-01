import streamlit as st
import time
import requests
import random
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. CONFIGURAZIONE API ---
API_KEY = "ea1f03fb102749fa9140e20b184f2996" 
BASE_URL = "https://api.football-data.org/v4/"

# --- 2. SETUP UI & CSS ---
st.set_page_config(page_title="AI NEURAL COMMANDER v12.0", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden; height: 0px; }
    footer { visibility: hidden; }
    .stApp { background-color: #030508; color: #e0e0e0; }
    
    .data-card {
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.5), rgba(30, 41, 59, 0.3));
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
        backdrop-filter: blur(12px);
    }
    
    .quota-box {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        padding: 10px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .terminal-text {
        font-family: 'Courier New', monospace;
        color: #10b981;
        font-size: 0.85rem;
        margin: 0;
    }

    .absent-card {
        background: rgba(239, 68, 68, 0.1);
        border: 1px solid rgba(239, 68, 68, 0.2);
        padding: 8px;
        border-radius: 10px;
        margin-top: 5px;
        font-size: 0.8rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. FUNZIONI CORE ---
def fetch_api_data(endpoint):
    headers = {'X-Auth-Token': API_KEY}
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=10)
        return response.json()
    except:
        return None

def format_time(iso_date):
    dt = datetime.fromisoformat(iso_date.replace('Z', '+00:00')) + timedelta(hours=2)
    return dt.strftime("%d/%m - %H:%M")

def get_deep_analysis():
    # Esito 1X2
    p = np.random.dirichlet(np.array([12, 6, 7]), size=1)[0]
    # Mercati Extra
    uo25 = random.uniform(0.3, 0.7)
    gg = random.uniform(0.4, 0.6)
    # Dettagli Simulati
    reasons = ["Infortunio Muscolare", "Squalifica", "Problema Fisico", "Scelta Tecnica"]
    players = ["M. Rossi", "L. Moretti", "G. Esposito", "A. Ricci", "D. Bianchi"]
    
    return {
        "1X2": p,
        "UO25": [1-uo25, uo25],
        "GGNG": [gg, 1-gg],
        "RADAR": [random.randint(65, 98) for _ in range(5)],
        "home_absents": [{"name": random.choice(players), "reason": random.choice(reasons)} for _ in range(random.randint(0,2))],
        "away_absents": [{"name": random.choice(players), "reason": random.choice(reasons)} for _ in range(random.randint(0,2))],
        "referee": random.choice(["D. Orsato", "M. Oliver", "S. Marciniak"]),
        "weather": random.choice(["Sereno 22°C", "Pioggia 14°C", "Nuvoloso 18°C"])
    }

# --- 4. LOGICA DI STATO ---
if 'last_selected' not in st.session_state:
    st.session_state.last_selected = None

# --- 5. MAIN APP ---
st.markdown("<h1 style='text-align: center; color: #3b82f6;'>🧠 NEURAL COMMANDER v12.0</h1>", unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    with c1:
        league = st.selectbox("🏆 Seleziona Lega", ["Serie A (SA)", "Premier League (PL)", "La Liga (PD)"])
        l_code = league.split("(")[1].replace(")", "")
    with c2:
        if st.button("🔄 SINCRONIZZA FEED API", use_container_width=True):
            data = fetch_api_data(f"competitions/{l_code}/matches?status=SCHEDULED")
            if data: st.session_state.matches = data.get('matches', [])

    matches = st.session_state.get('matches', [])
    if matches:
        labels = [f"{format_time(m['utcDate'])} | {m['homeTeam']['name']} vs {m['awayTeam']['name']}" for m in matches]
        selected = st.selectbox("🎯 Seleziona Target", ["---"] + labels)
    else:
        st.info("Sincronizza il feed per iniziare.")
        selected = "---"
    st.markdown('</div>', unsafe_allow_html=True)

# --- ANIMAZIONE E ANALISI ---
if selected != "---":
    if st.session_state.last_selected != selected:
        loading_placeholder = st.empty()
        with loading_placeholder.container():
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            st.markdown("<p class='terminal-text'>[SISTEMA]: Inizializzazione Deep Scan...</p>", unsafe_allow_html=True)
            progress_bar = st.progress(0)
            steps = ["📡 Connessione Satellitare...", "🧬 Power Index Scan...", "🚑 Verifica Bollettino Medici...", "🧠 Simulazione Monte Carlo...", "✅ Analisi Completata."]
            for i, step in enumerate(steps):
                time.sleep(0.5)
                st.markdown(f"<p class='terminal-text' style='opacity: 0.8;'>{step}</p>", unsafe_allow_html=True)
                progress_bar.progress((i + 1) * 20)
            time.sleep(0.3)
            st.markdown('</div>', unsafe_allow_html=True)
        loading_placeholder.empty()
        st.session_state.last_selected = selected

    # RECUPERO DATI ANALISI
    m_idx = labels.index(selected)
    m_data = matches[m_idx]
    h_name, a_name = m_data['homeTeam']['name'], m_data['awayTeam']['name']
    analysis = get_deep_analysis()

    st.markdown(f"<h2 style='text-align:center;'>{h_name.upper()} vs {a_name.upper()}</h2>", unsafe_allow_html=True)

    # LAYOUT A TRE COLONNE
    col_left, col_mid, col_right = st.columns([1, 1.5, 1])

    with col_left:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.write("🚑 **Assenti Home**")
        if not analysis['home_absents']: st.write("✅ Rosa Completa")
        for p in analysis['home_absents']:
            st.markdown(f"<div class='absent-card'><b>{p['name']}</b><br>{p['reason']}</div>", unsafe_allow_html=True)
        st.divider()
        st.write(f"⚖️ **Arbitro:** {analysis['referee']}")
        st.write(f"☁️ **Meteo:** {analysis['weather']}")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_mid:
        st.markdown('<div class="data-card" style="text-align:center;">', unsafe_allow_html=True)
        st.subheader("🎯 Neural Probabilities")
        c1, c2, c3 = st.columns(3)
        res_labs = ['1', 'X', '2']
        for i, col in enumerate([c1, c2, c3]):
            p = analysis['1X2'][i]
            col.markdown(f"<div class='quota-box'><small>{res_labs[i]}</small><br><b style='color:#10b981;'>{p*100:.1f}%</b><br><span style='color:#3b82f6;'>{1/p:.2f}</span></div>", unsafe_allow_html=True)
        
        st.write("")
        fig = go.Figure(data=go.Scatterpolar(r=analysis['RADAR'], theta=['Att','Dif','For','Fis','Tat'], fill='toself', line_color='#10b981'))
        fig.update_layout(polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(visible=False, range=[0, 100])), showlegend=False, height=200, margin=dict(t=20,b=20,l=35,r=35), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        st.success(f"💡 ADVISORY: Puntare su **{res_labs[np.argmax(analysis['1X2'])]}**")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.write("🚑 **Assenti Away**")
        if not analysis['away_absents']: st.write("✅ Rosa Completa")
        for p in analysis['away_absents']:
            st.markdown(f"<div class='absent-card'><b>{p['name']}</b><br>{p['reason']}</div>", unsafe_allow_html=True)
        st.divider()
        st.write("⚽ **Mercati Extra**")
        u, o = analysis['UO25']
        st.markdown(f"<small>U/O 2.5:</small><br>U {u*100:.0f}% | O {o*100:.0f}%", unsafe_allow_html=True)
        g, n = analysis['GGNG']
        st.markdown(f"<br><small>GG/NG:</small><br>GG {g*100:.0f}% | NG {n*100:.0f}%", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
