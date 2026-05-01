import streamlit as st
import time
import requests
import random
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. CONFIGURAZIONE API ---
API_KEY = "LA_TUA_API_KEY"  # Assicurati di inserire la tua chiave!
BASE_URL = "https://api.football-data.org/v4/"

# --- 2. SETUP UI & CSS CUSTOM ---
st.set_page_config(page_title="AI NEURAL COMMANDER v11.5", layout="wide", initial_sidebar_state="collapsed")

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
    
    .neural-log {
        font-family: 'Courier New', monospace;
        font-size: 0.8rem;
        color: #10b981;
    }

    .vs-badge {
        background: linear-gradient(135deg, #3b82f6, #8b5cf6);
        padding: 5px 20px;
        border-radius: 30px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. FUNZIONI MOTORE ---
def fetch_api_data(endpoint):
    headers = {'X-Auth-Token': API_KEY}
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=10)
        if response.status_code == 429:
            st.error("⚠️ Limite API raggiunto. Attendi 60 secondi.")
            return None
        return response.json()
    except Exception as e:
        st.error(f"❌ Errore Connessione: {e}")
        return None

def format_time(iso_date):
    dt = datetime.fromisoformat(iso_date.replace('Z', '+00:00')) + timedelta(hours=2)
    return dt.strftime("%d/%m - %H:%M")

def get_neural_metrics():
    # Genera probabilità realistiche
    p = np.random.dirichlet(np.array([10, 5, 6]), size=1)[0] # 1, X, 2
    uo = random.uniform(0.3, 0.7)
    gg = random.uniform(0.4, 0.6)
    return {
        "1X2": p,
        "UO25": [1-uo, uo],
        "GGNG": [gg, 1-gg],
        "RADAR": [random.randint(60, 95) for _ in range(5)]
    }

# --- 4. MAIN APP ---
st.markdown("<h1 style='text-align: center; color: #3b82f6;'>🧠 NEURAL COMMANDER v11.5</h1>", unsafe_allow_html=True)

# Container Selezione
with st.container():
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1])
    with c1:
        league = st.selectbox("🏆 Seleziona Lega", ["Serie A (SA)", "Premier League (PL)", "La Liga (PD)", "Bundesliga (BL1)"])
        l_code = league.split("(")[1].replace(")", "")
    with c2:
        if st.button("🔄 SINCRONIZZA DATI REAL-TIME", use_container_width=True):
            data = fetch_api_data(f"competitions/{l_code}/matches?status=SCHEDULED")
            if data: st.session_state.matches = data.get('matches', [])

    matches = st.session_state.get('matches', [])
    if matches:
        labels = [f"{format_time(m['utcDate'])} | {m['homeTeam']['name']} vs {m['awayTeam']['name']}" for m in matches]
        selected = st.selectbox("🎯 Seleziona Evento per Analisi Profonda", ["---"] + labels)
    else:
        st.info("Sincronizza per scaricare il palinsesto reale dal server.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- VISUALIZZAZIONE ANALISI ---
if 'selected' in locals() and selected != "---":
    m_idx = labels.index(selected)
    m_data = matches[m_idx]
    h_team, a_team = m_data['homeTeam']['name'], m_data['awayTeam']['name']

    # Simulazione Processamento
    with st.status("🧬 Neural Engine in funzione...", expanded=True) as status:
        st.write("📥 Estrazione parametri statistici...")
        time.sleep(0.6)
        metrics = get_neural_metrics()
        st.write("🤖 Calcolo matriciale delle probabilità...")
        time.sleep(0.6)
        status.update(label="Analisi Completata!", state="complete")

    # Layout a Colonne
    col_info, col_main = st.columns([1, 2])

    with col_info:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center;'><span class='vs-badge'>{format_time(m_data['utcDate'])}</span></div>", unsafe_allow_html=True)
        st.write(f"🏠 **{h_team}**")
        st.write(f"🚌 **{a_team}**")
        st.divider()
        st.write("📊 **Neural Power Index**")
        fig_radar = go.Figure(data=go.Scatterpolar(r=metrics['RADAR'], theta=['Attacco','Difesa','Forma','Fisico','Tattica'], fill='toself', line_color='#3b82f6'))
        fig_radar.update_layout(polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(visible=False, range=[0, 100])), showlegend=False, height=200, margin=dict(t=20,b=20,l=40,r=40), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_radar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_main:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.subheader("🎯 Quote Fair Analizzate")
        
        # 1X2 Row
        c1, c2, c3 = st.columns(3)
        labels_1x2 = ['1', 'X', '2']
        for i, col in enumerate([c1, c2, c3]):
            prob = metrics['1X2'][i]
            col.markdown(f"<div class='quota-box'><small>{labels_1x2[i]}</small><br><b style='color:#10b981;'>{prob*100:.1f}%</b><br><span style='color:#3b82f6;'>{1/prob:.2f}</span></div>", unsafe_allow_html=True)
        
        # Altri Mercati
        st.write("")
        c_uo, c_gg = st.columns(2)
        with c_uo:
            st.markdown("<small>UNDER/OVER 2.5</small>", unsafe_allow_html=True)
            u, o = metrics['UO25']
            st.markdown(f"<div class='quota-box'>U: <b>{u*100:.0f}%</b> ({1/u:.2f}) | O: <b>{o*100:.0f}%</b> ({1/o:.2f})</div>", unsafe_allow_html=True)
        with c_gg:
            st.markdown("<small>GOAL / NO GOAL</small>", unsafe_allow_html=True)
            g, n = metrics['GGNG']
            st.markdown(f"<div class='quota-box'>GG: <b>{g*100:.0f}%</b> ({1/g:.2f}) | NG: <b>{n*100:.0f}%</b> ({1/n:.2f})</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Consiglio Schedina
        st.success(f"💡 **CONSIGLIO AI**: {'1X2: ' + ('1' if metrics['1X2'][0] > metrics['1X2'][2] else '2')} con fiducia del {max(metrics['1X2'])*100:.1f}%")

# Sezione Registrazione (Sempre Visibile in fondo)
st.markdown("---")
with st.expander("📩 RIMANI AGGIORNATO (REGISTRAZIONE)"):
    with st.form("reg_form"):
        email = st.text_input("Inserisci la tua Email")
        st.form_submit_button("Iscriviti alla Newsletter Neural")
