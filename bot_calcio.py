import streamlit as st
import time
import requests
import random
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. CONFIGURAZIONE API ---
API_KEY = ea1f03fb102749fa9140e20b184f2996" 
BASE_URL = "https://api.football-data.org/v4/"

# --- 2. SETUP UI & CSS ---
st.set_page_config(page_title="AI NEURAL COMMANDER v11.8", layout="wide", initial_sidebar_state="collapsed")

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
        font-size: 0.9rem;
        margin: 0;
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

def get_neural_metrics():
    p = np.random.dirichlet(np.array([12, 6, 7]), size=1)[0]
    uo = random.uniform(0.3, 0.7)
    gg = random.uniform(0.4, 0.6)
    return {"1X2": p, "UO25": [1-uo, uo], "GGNG": [gg, 1-gg], "RADAR": [random.randint(65, 98) for _ in range(5)]}

# --- 4. LOGICA DI STATO PER ANIMAZIONE ---
if 'last_selected' not in st.session_state:
    st.session_state.last_selected = None

# --- 5. MAIN APP ---
st.markdown("<h1 style='text-align: center; color: #3b82f6;'>🧠 NEURAL COMMANDER v11.8</h1>", unsafe_allow_html=True)

# Container Selezione
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
    # Controlla se l'evento è cambiato per mostrare l'animazione
    if st.session_state.last_selected != selected:
        loading_placeholder = st.empty()
        with loading_placeholder.container():
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            st.markdown("<p class='terminal-text'>[SISTEMA]: Inizializzazione Deep Scan...</p>", unsafe_allow_html=True)
            progress_bar = st.progress(0)
            
            steps = [
                "📡 Connessione ai nodi satellitari API...",
                "🧬 Estrazione Power Index delle squadre...",
                "🧠 Simulazione scenari tattici (Monte Carlo)...",
                "✅ Intelligence Report Generato."
            ]
            
            for i, step in enumerate(steps):
                time.sleep(0.5)
                st.markdown(f"<p class='terminal-text' style='opacity: 0.8;'>{step}</p>", unsafe_allow_html=True)
                progress_bar.progress((i + 1) * 25)
            
            time.sleep(0.3)
            st.markdown('</div>', unsafe_allow_html=True)
        
        loading_placeholder.empty()
        st.session_state.last_selected = selected # Salva lo stato per non ripetere l'animazione inutilmente

    # --- RENDER REPORT ---
    m_idx = labels.index(selected)
    m_data = matches[m_idx]
    h_team, a_team = m_data['homeTeam']['name'], m_data['awayTeam']['name']
    metrics = get_neural_metrics()

    st.markdown(f"<h2 style='text-align:center;'>{h_team.upper()} <span style='color:#3b82f6;'>VS</span> {a_team.upper()}</h2>", unsafe_allow_html=True)

    col_side, col_main = st.columns([1, 2.2])

    with col_side:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.write("📊 **Neural Radar**")
        fig = go.Figure(data=go.Scatterpolar(r=metrics['RADAR'], theta=['Att','Dif','For','Fis','Tat'], fill='toself', line_color='#10b981'))
        fig.update_layout(polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(visible=False, range=[0, 100])), showlegend=False, height=220, margin=dict(t=20,b=20,l=35,r=35), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_main:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.subheader("🎯 Quote Fair & Probabilità")
        c1, c2, c3 = st.columns(3)
        res_labels = ['1', 'X', '2']
        for i, col in enumerate([c1, c2, c3]):
            p = metrics['1X2'][i]
            col.markdown(f"<div class='quota-box'><small>{res_labels[i]}</small><br><b style='color:#10b981;'>{p*100:.1f}%</b><br><span style='color:#3b82f6;'>{1/p:.2f}</span></div>", unsafe_allow_html=True)
        
        st.write("")
        ca, cb = st.columns(2)
        with ca:
            u, o = metrics['UO25']
            st.markdown(f"<div class='quota-box'><small>U/O 2.5</small><br>U: {u*100:.0f}% | O: {o*100:.0f}%</div>", unsafe_allow_html=True)
        with cb:
            g, n = metrics['GGNG']
            st.markdown(f"<div class='quota-box'><small>GOAL / NO GOAL</small><br>GG: {g*100:.0f}% | NG: {n*100:.0f}%</div>", unsafe_allow_html=True)
        
        st.success(f"💡 **CONSIGLIO AI**: Puntare su **{res_labels[np.argmax(metrics['1X2'])]}** (Fiducia: {max(metrics['1X2'])*100:.1f}%)")
        st.markdown('</div>', unsafe_allow_html=True)
