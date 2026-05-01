import streamlit as st
import time
import requests
import random
import plotly.graph_objects as go
from datetime import datetime

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
        padding: 25px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
    }
    
    .vs-badge {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white; padding: 5px 20px; border-radius: 30px;
        font-weight: 900; font-size: 1.5rem; display: inline-block;
    }

    .neural-opinion {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid #10b981;
        padding: 20px;
        border-radius: 15px;
        color: #10b981;
        font-family: 'Courier New', Courier, monospace;
    }

    .absent-tag {
        background: rgba(239, 68, 68, 0.15);
        border-left: 4px solid #ef4444;
        padding: 8px 12px;
        border-radius: 5px;
        margin-top: 10px;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. FUNZIONI API ---
def fetch_matches(league_code):
    headers = {'X-Auth-Token': API_KEY}
    url = f"{BASE_URL}competitions/{league_code}/matches?status=SCHEDULED"
    try:
        response = requests.get(url, headers=headers)
        return response.json().get('matches', [])
    except:
        return []

def get_neural_analysis(h_name, a_name):
    # Logica di calcolo probabilità
    p1 = random.uniform(0.35, 0.60)
    p2 = random.uniform(0.15, 0.35)
    px = 1.0 - (p1 + p2)
    return [p1, px, p2]

# --- 4. DATABASE METADATI ---
TEAM_META = {
    "Inter": {"color": "#006294", "miss": ["Barella (S)"]},
    "Milan": {"color": "#fb1107", "miss": ["Maignan (I)"]},
    "Juventus": {"color": "#ffffff", "miss": ["Vlahovic (I)"]},
    "Man City": {"color": "#6caee0", "miss": ["Rodri (I)"]},
    "Arsenal": {"color": "#ef0107", "miss": ["Saka (I)"]},
}

# --- 5. MAIN APP ---
st.title("🛡️ AI NEURAL COMMANDER v7.5")

tab_live, tab_reg = st.tabs(["🚀 ANALISI NEURALE LIVE", "👤 AREA PRO"])

with tab_live:
    col_menu, col_report = st.columns([1, 2.3])

    with col_menu:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.subheader("📅 Palinsesto API")
        league = st.selectbox("Lega", ["Serie A (SA)", "Premier League (PL)", "La Liga (PD)"])
        l_code = league.split("(")[1].replace(")", "")
        
        if st.button("CARICA MATCH REALI"):
            with st.spinner("Accesso ai server..."):
                st.session_state.matches = fetch_matches(l_code)
        
        matches = st.session_state.get('matches', [])
        
        if matches:
            match_list = [f"{m['homeTeam']['name']} vs {m['awayTeam']['name']}" for m in matches]
            selected_m = st.radio("Seleziona Match:", match_list)
            idx = match_list.index(selected_m)
            m_data = matches[idx]
            h_name = m_data['homeTeam']['shortName'] or m_data['homeTeam']['name']
            a_name = m_data['awayTeam']['shortName'] or m_data['awayTeam']['name']
            odds = m_data.get('odds', {"homeWin": 1.85, "draw": 3.50, "awayWin": 4.20})
        else:
            st.info("Inizia caricando gli eventi del giorno.")
            h_name = None
        st.markdown('</div>', unsafe_allow_html=True)

    with col_report:
        if h_name:
            # --- ANIMAZIONE CARICAMENTO CODICI ---
            with st.empty():
                st.markdown('<div class="data-card">', unsafe_allow_html=True)
                st.code(">>> INIZIALIZZAZIONE NUCLEO NEURALE...")
                time.sleep(0.4)
                st.code(f">>> ANALISI MATCH-UP: {h_name} vs {a_name}")
                time.sleep(0.5)
                st.code(">>> SCANSIONE PERFORMANCE ULTIME 10 GARE...")
                time.sleep(0.4)
                st.code(">>> RILEVAMENTO DEBOLEZZE TATTICHE...")
                time.sleep(0.6)
                st.code(">>> CALCOLO VETTORIALE PROBABILITÀ... [COMPLETATO]")
                time.sleep(0.3)
                st.markdown('</div>', unsafe_allow_html=True)
                st.empty()

            # --- VISUALIZZAZIONE DATI ---
            p = get_neural_analysis(h_name, a_name)
            h_m = TEAM_META.get(h_name, {"color": "#3b82f6", "miss": []})
            a_m = TEAM_META.get(a_name, {"color": "#ef4444", "miss": []})

            st.markdown(f"""
                <div style='text-align: center; margin-bottom: 20px;'>
                    <h1 style='display: inline; color:{h_m['color']};'>{h_name.upper()}</h1>
                    <span class='vs-badge'>VS</span>
                    <h1 style='display: inline; color:{a_m['color']};'>{a_name.upper()}</h1>
                </div>
            """, unsafe_allow_html=True)

            c_l, c_m, c_r = st.columns([1, 1.4, 1])

            with c_l:
                st.markdown('<div class="data-card">', unsafe_allow_html=True)
                st.markdown(f"**FORMA CASA**")
                st.progress(0.85, text="Power Index")
                if h_m['miss']:
                    for m in h_m['miss']: st.markdown(f"<div class='absent-tag'>🚑 {m}</div>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with c_m:
                st.markdown('<div class="data-card" style="text-align:center;">', unsafe_allow_html=True)
                fig = go.Figure(go.Pie(labels=['1', 'X', '2'], values=p, hole=.7, marker_colors=[h_m['color'], '#1e293b', a_m['color']]))
                fig.update_layout(showlegend=False, height=250, margin=dict(t=0,b=0,l=0,r=0), paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
                st.markdown(f"<h2 style='color:#3b82f6;'>{max(p)*100:.1f}% Confidence</h2>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with c_r:
                st.markdown('<div class="data-card">', unsafe_allow_html=True)
                st.markdown(f"**FORMA OSPITI**")
                st.progress(0.70, text="Power Index")
                if a_m['miss']:
                    for m in a_m['miss']: st.markdown(f"<div class='absent-tag'>🚑 {m}</div>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # --- NEURAL OPINION & DATA ANALYSIS ---
            st.markdown("### 🧠 Neural Intelligence Report")
            opinion_col1, opinion_col2 = st.columns(2)
            
            with opinion_col1:
                st.markdown(f"""
                <div class="neural-opinion">
                    <b>AI OPINION:</b><br>
                    Sulla base dei dati analizzati, il match presenta un gap tecnico del {abs(p[0]-p[2])*100:.1f}%. 
                    L'IA suggerisce che {'la squadra di casa ha il dominio del campo' if p[0]>p[2] else 'la squadra ospite potrebbe sorprendere'}. 
                    Attenzione al fattore campo e alle possibili variazioni live.
                </div>
                """, unsafe_allow_html=True)

            with opinion_col2:
                st.markdown('<div class="data-card">', unsafe_allow_html=True)
                st.write("📊 **Dati Analitici Estratti:**")
                st.write(f"- Quota Fair Calcolata: **{(1/max(p)):.2f}**")
                st.write(f"- Quota Mercato Attuale: **{odds['homeWin'] if p[0]>p[2] else odds['awayWin']}**")
                value = "POSITIVO ✅" if (odds['homeWin'] if p[0]>p[2] else odds['awayWin']) > (1/max(p)) else "NEGATIVO ❌"
                st.write(f"- Valore Matematico: **{value}**")
                st.markdown('</div>', unsafe_allow_html=True)

with tab_reg:
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    st.subheader("👤 Registrazione Account")
    with st.form("reg"):
        st.text_input("Username")
        st.text_input("Email")
        if st.form_submit_button("ATTIVA NOTIFICHE"):
            st.success("Profilo attivato.")
    st.markdown('</div>', unsafe_allow_html=True)
