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
st.set_page_config(page_title="AI NEURAL COMMANDER v13.0", layout="wide", initial_sidebar_state="collapsed")

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
    
    .schedina-card {
        background: rgba(59, 130, 246, 0.1);
        border: 1px dashed #3b82f6;
        border-radius: 15px;
        padding: 15px;
    }

    .quota-button {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        cursor: pointer;
        transition: 0.3s;
    }
    .quota-button:hover { border-color: #10b981; background: rgba(16, 185, 129, 0.1); }
    </style>
""", unsafe_allow_html=True)

# --- 3. INIZIALIZZAZIONE SESSION STATE (SCHEDINA) ---
if 'schedina' not in st.session_state:
    st.session_state.schedina = []
if 'matches' not in st.session_state:
    st.session_state.matches = []
if 'last_selected' not in st.session_state:
    st.session_state.last_selected = None

# --- 4. FUNZIONI CORE ---
def fetch_api_data(endpoint):
    headers = {'X-Auth-Token': API_KEY}
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers, timeout=10)
        return response.json()
    except: return None

def format_time(iso_date):
    dt = datetime.fromisoformat(iso_date.replace('Z', '+00:00')) + timedelta(hours=2)
    return dt.strftime("%d/%m - %H:%M")

def get_deep_analysis():
    p = np.random.dirichlet(np.array([12, 6, 7]), size=1)[0]
    return {
        "1X2": p,
        "UO25": [random.uniform(0.3, 0.7), random.uniform(0.3, 0.7)],
        "RADAR": [random.randint(65, 98) for _ in range(5)]
    }

# --- 5. MAIN APP ---
st.markdown("<h1 style='text-align: center; color: #3b82f6;'>🧠 NEURAL COMMANDER v13.0</h1>", unsafe_allow_html=True)

# Sidebar Schedina (Visualizzazione su Mobile in alto o basso)
with st.sidebar:
    st.header("📋 La Tua Schedina")
    if not st.session_state.schedina:
        st.write("Nessun evento selezionato.")
    else:
        moltiplicatore = 1.0
        for i, bet in enumerate(st.session_state.schedina):
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.05); padding:10px; border-radius:10px; margin-bottom:5px;">
                <small>{bet['match']}</small><br>
                <b>{bet['segno']}</b> @ {bet['quota']:.2f}
            </div>
            """, unsafe_allow_html=True)
            moltiplicatore *= bet['quota']
        
        st.divider()
        st.subheader(f"Totale: {moltiplicatore:.2f}")
        if st.button("Svuota Schedina"):
            st.session_state.schedina = []
            st.rerun()

# Layout Principale
col_main, col_spacer = st.columns([3, 0.1])

with col_main:
    # Selezione Evento
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        league = st.selectbox("🏆 Campionato", ["Serie A (SA)", "Premier League (PL)", "La Liga (PD)"])
        l_code = league.split("(")[1].replace(")", "")
    with c2:
        if st.button("🔄 SINCRONIZZA FEED API", use_container_width=True):
            data = fetch_api_data(f"competitions/{l_code}/matches?status=SCHEDULED")
            if data: st.session_state.matches = data.get('matches', [])

    matches = st.session_state.get('matches', [])
    if matches:
        labels = [f"{format_time(m['utcDate'])} | {m['homeTeam']['name']} vs {m['awayTeam']['name']}" for m in matches]
        selected = st.selectbox("🎯 Analizza e Scommetti", ["---"] + labels)
    else:
        st.info("Sincronizza per caricare i match.")
        selected = "---"
    st.markdown('</div>', unsafe_allow_html=True)

    if selected != "---":
        # Gestione Animazione
        if st.session_state.last_selected != selected:
            with st.status("🧬 Deep Scanning...", expanded=True):
                time.sleep(1.0)
            st.session_state.last_selected = selected

        m_idx = labels.index(selected)
        m_data = matches[m_idx]
        h_name, a_name = m_data['homeTeam']['name'], m_data['awayTeam']['name']
        analysis = get_deep_analysis()

        # Render Analisi
        st.markdown(f"<h2 style='text-align:center;'>{h_team if 'h_team' in locals() else h_name} vs {a_team if 'a_team' in locals() else a_name}</h2>", unsafe_allow_html=True)
        
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.subheader("🎯 Seleziona l'esito da salvare:")
        
        c1, c2, c3 = st.columns(3)
        res_labs = ['1', 'X', '2']
        
        for i, col in enumerate([c1, c2, c3]):
            prob = analysis['1X2'][i]
            quota = 1/prob
            with col:
                if st.button(f"{res_labs[i]} @ {quota:.2f}", key=f"bet_{i}", use_container_width=True):
                    new_bet = {
                        "match": f"{h_name}-{a_name}",
                        "segno": res_labs[i],
                        "quota": quota
                    }
                    st.session_state.schedina.append(new_bet)
                    st.success(f"Aggiunto: {res_labs[i]}")
        
        st.write("")
        st.info("💡 Consiglio AI: L'analisi suggerisce una quota fair di " + f"{1/max(analysis['1X2']):.2f}")
        st.markdown('</div>', unsafe_allow_html=True)

        # Radar Chart Dettagli
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        fig = go.Figure(data=go.Scatterpolar(r=analysis['RADAR'], theta=['Att','Dif','For','Fis','Tat'], fill='toself', line_color='#3b82f6'))
        fig.update_layout(polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(visible=False, range=[0, 100])), showlegend=False, height=250, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
