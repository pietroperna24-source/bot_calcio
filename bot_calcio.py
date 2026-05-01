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
st.set_page_config(page_title="AI NEURAL COMMANDER v14.0", layout="wide", initial_sidebar_state="collapsed")

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
    
    .terminal-text { font-family: 'Courier New', monospace; color: #10b981; font-size: 0.85rem; margin: 0; }
    
    .bet-row {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
        border-left: 5px solid #3b82f6;
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

# --- 3. INIZIALIZZAZIONE STATO ---
if 'schedina' not in st.session_state: st.session_state.schedina = []
if 'matches' not in st.session_state: st.session_state.matches = []
if 'last_selected' not in st.session_state: st.session_state.last_selected = None

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
    uo = random.uniform(0.3, 0.7)
    gg = random.uniform(0.4, 0.6)
    players = ["M. Rossi", "L. Moretti", "G. Esposito", "A. Ricci", "D. Bianchi"]
    reasons = ["Infortunio", "Squalifica", "Dubbio"]
    return {
        "1X2": p, "UO25": [1-uo, uo], "GGNG": [gg, 1-gg],
        "RADAR": [random.randint(65, 98) for _ in range(5)],
        "h_abs": [{"n": random.choice(players), "r": random.choice(reasons)} for _ in range(random.randint(0,2))],
        "a_abs": [{"n": random.choice(players), "r": random.choice(reasons)} for _ in range(random.randint(0,2))],
        "ref": random.choice(["D. Orsato", "M. Oliver", "S. Marciniak"]),
        "wet": random.choice(["Sereno 22°C", "Pioggia 14°C", "Nuvoloso 18°C"])
    }

# --- 5. MAIN APP ---
st.markdown("<h1 style='text-align: center; color: #3b82f6;'>🧠 NEURAL COMMANDER v14.0</h1>", unsafe_allow_html=True)

# Creazione della lista a parte tramite Tab
tab_analisi, tab_schedina = st.tabs(["🚀 ANALISI LIVE", "📝 LA MIA SCHEDINA"])

# --- TAB 1: ANALISI ---
with tab_analisi:
    with st.container():
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1])
        with c1:
            league = st.selectbox("🏆 Lega", ["Serie A (SA)", "Premier League (PL)", "La Liga (PD)"])
            l_code = league.split("(")[1].replace(")", "")
        with c2:
            if st.button("🔄 SINCRONIZZA FEED API", use_container_width=True):
                data = fetch_api_data(f"competitions/{l_code}/matches?status=SCHEDULED")
                if data: st.session_state.matches = data.get('matches', [])

        matches = st.session_state.get('matches', [])
        if matches:
            labels = [f"{format_time(m['utcDate'])} | {m['homeTeam']['name']} vs {m['awayTeam']['name']}" for m in matches]
            selected = st.selectbox("🎯 Seleziona Target da analizzare", ["---"] + labels)
        else:
            st.info("Sincronizza il feed per iniziare.")
            selected = "---"
        st.markdown('</div>', unsafe_allow_html=True)

    if selected != "---":
        if st.session_state.last_selected != selected:
            loading_placeholder = st.empty()
            with loading_placeholder.container():
                st.markdown('<div class="data-card">', unsafe_allow_html=True)
                st.markdown("<p class='terminal-text'>[SISTEMA]: Avvio Analisi...</p>", unsafe_allow_html=True)
                pb = st.progress(0)
                steps = ["📡 Connessione Satellitare...", "🧬 Power Index Scan...", "🚑 Controllo Infermeria...", "✅ Analisi Completata."]
                for i, s in enumerate(steps):
                    time.sleep(0.4)
                    st.markdown(f"<p class='terminal-text' style='opacity:0.7;'>{s}</p>", unsafe_allow_html=True)
                    pb.progress((i+1)*25)
                st.markdown('</div>', unsafe_allow_html=True)
            loading_placeholder.empty()
            st.session_state.last_selected = selected

        # Dati Analisi
        m_data = matches[labels.index(selected)]
        h_n, a_n = m_data['homeTeam']['name'], m_data['awayTeam']['name']
        res = get_deep_analysis()

        st.markdown(f"<h2 style='text-align:center;'>{h_n.upper()} vs {a_n.upper()}</h2>", unsafe_allow_html=True)

        col_l, col_m, col_r = st.columns([1, 1.5, 1])

        with col_l:
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            st.write("🚑 **Assenti Home**")
            if not res['h_abs']: st.write("✅ Nessuno")
            for p in res['h_abs']: st.markdown(f"<div class='absent-card'><b>{p['n']}</b><br>{p['r']}</div>", unsafe_allow_html=True)
            st.divider()
            st.write(f"⚖️ {res['ref']}")
            st.write(f"☁️ {res['wet']}")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_m:
            st.markdown('<div class="data-card" style="text-align:center;">', unsafe_allow_html=True)
            st.subheader("🎯 Neural Betting (Clicca per aggiungere)")
            c1, c2, c3 = st.columns(3)
            labs = ['1', 'X', '2']
            for i, col in enumerate([c1, c2, c3]):
                q = 1/res['1X2'][i]
                with col:
                    if st.button(f"{labs[i]} @ {q:.2f}", key=f"btn_{i}", use_container_width=True):
                        st.session_state.schedina.append({"m": f"{h_n}-{a_n}", "s": labs[i], "q": q})
                        st.toast(f"✅ {labs[i]} aggiunto!")
            
            fig = go.Figure(data=go.Scatterpolar(r=res['RADAR'], theta=['Att','Dif','For','Fis','Tat'], fill='toself', line_color='#10b981'))
            fig.update_layout(polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(visible=False, range=[0, 100])), showlegend=False, height=200, margin=dict(t=20,b=20,l=35,r=35), paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_r:
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            st.write("🚑 **Assenti Away**")
            if not res['a_abs']: st.write("✅ Nessuno")
            for p in res['a_abs']: st.markdown(f"<div class='absent-card'><b>{p['n']}</b><br>{p['r']}</div>", unsafe_allow_html=True)
            st.divider()
            st.write("⚽ **Extra Markets**")
            u, o = res['UO25']
            if st.button(f"U 2.5 @ {1/u:.2f}", use_container_width=True): 
                st.session_state.schedina.append({"m": f"{h_n}-{a_n}", "s": "Under 2.5", "q": 1/u})
            if st.button(f"O 2.5 @ {1/o:.2f}", use_container_width=True): 
                st.session_state.schedina.append({"m": f"{h_n}-{a_n}", "s": "Over 2.5", "q": 1/o})
            st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: LA SCHEDINA (LISTA A PARTE) ---
with tab_schedina:
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    st.subheader("📋 Riepilogo Scommesse Selezionate")
    
    if not st.session_state.schedina:
        st.warning("Non hai ancora selezionato alcun evento. Torna nella sezione Analisi e clicca sulle quote.")
    else:
        total_odd = 1.0
        for i, bet in enumerate(st.session_state.schedina):
            col_info, col_del = st.columns([4, 1])
            with col_info:
                st.markdown(f"""
                <div class="bet-row">
                    <span style="color:#94a3b8; font-size:0.8rem;">EVENTO:</span> <b>{bet['m']}</b><br>
                    <span style="color:#3b82f6; font-size:1rem;">SEGNO: {bet['s']}</span> | <span style="color:#10b981;">QUOTA: {bet['q']:.2f}</span>
                </div>
                """, unsafe_allow_html=True)
            with col_del:
                if st.button("❌ Rimuovi", key=f"del_{i}"):
                    st.session_state.schedina.pop(i)
                    st.rerun()
            total_odd *= bet['q']
        
        st.divider()
        c_res1, c_res2 = st.columns(2)
        with c_res1:
            st.metric("MOLTIPLICATORE TOTALE", f"x {total_odd:.2f}")
        with c_res2:
            importo = st.number_input("Quanto vuoi puntare? (€)", min_value=2, value=5)
            st.success(f"VINCITA POTENZIALE: **{(total_odd * importo):.2f} €**")
        
        if st.button("🗑️ SVUOTA TUTTA LA SCHEDINA", use_container_width=True):
            st.session_state.schedina = []
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
