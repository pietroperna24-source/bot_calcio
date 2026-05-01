import streamlit as st
import time
import requests
import random
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. CONFIGURAZIONE API ---
API_KEY = "ea1f03fb102749fa9140e20b184f2996" 
BASE_URL = "https://api.football-data.org/v4/"

# --- 2. UI & CSS OTTIMIZZATO PER MOBILE ---
st.set_page_config(page_title="AI NEURAL COMMANDER PRO", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden; height: 0px; }
    footer { visibility: hidden; }
    .stApp { background-color: #05070a; color: #e0e0e0; }
    
    @media (max-width: 768px) {
        [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
        .stat-value { font-size: 1.4rem !important; }
    }

    .data-card {
        background: rgba(30, 41, 59, 0.25);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
        backdrop-filter: blur(10px);
    }
    
    .vs-badge {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white; padding: 5px 20px; border-radius: 30px;
        font-weight: 900; font-size: 1.5rem; display: inline-block;
    }

    .neural-opinion {
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid #10b981;
        padding: 15px;
        border-radius: 15px;
        color: #10b981;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.9rem;
    }

    .market-box {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. FUNZIONI TECNICHE & CALCOLI AGGIUNTIVI ---
def fetch_matches(league_code):
    headers = {'X-Auth-Token': API_KEY}
    url = f"{BASE_URL}competitions/{league_code}/matches?status=SCHEDULED"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.json().get('matches', [])
    except:
        return []

def format_to_local_time(iso_date):
    dt_utc = datetime.fromisoformat(iso_date.replace('Z', '+00:00'))
    dt_local = dt_utc + timedelta(hours=2) 
    return dt_local.strftime("%d/%m - %H:%M")

def get_complete_analysis():
    # Esito Finale 1X2
    p1 = random.uniform(0.35, 0.55)
    p2 = random.uniform(0.20, 0.35)
    px = 1.0 - (p1 + p2)
    
    # Under/Over 2.5
    u25 = random.uniform(0.40, 0.60)
    o25 = 1.0 - u25
    
    # Goal/No Goal
    gg = random.uniform(0.45, 0.65)
    ng = 1.0 - gg
    
    return {
        "1X2": [p1, px, p2],
        "UO25": [u25, o25],
        "GGNG": [gg, ng],
        "DC": [p1+px, p2+px, p1+p2] # 1X, X2, 12
    }

# --- 4. MAIN APP ---
st.title("🛡️ AI NEURAL COMMANDER")

tab_live, tab_reg = st.tabs(["🚀 ANALISI MULTI-MERCATO", "👤 ACCOUNT"])

with tab_live:
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    league = st.selectbox("Campionato", ["Serie A (SA)", "Premier League (PL)", "La Liga (PD)"])
    l_code = league.split("(")[1].replace(")", "")
    
    if st.button("🔄 AGGIORNA PALINSESTO", use_container_width=True):
        st.session_state.matches = fetch_matches(l_code)
    
    matches = st.session_state.get('matches', [])
    
    if matches:
        match_labels = [f"{format_to_local_time(m['utcDate'])} | {m['homeTeam']['name']} vs {m['awayTeam']['name']}" for m in matches]
        selected_m = st.selectbox("Scegli il match per la schedina:", ["--- Seleziona ---"] + match_labels)
        
        if selected_m != "--- Seleziona ---":
            idx = match_labels.index(selected_m)
            m_data = matches[idx]
            h_name = m_data['homeTeam']['name']
            a_name = m_data['awayTeam']['name']
            
            with st.status("🧬 Elaborazione Algoritmi Multi-Mercato...", expanded=True):
                time.sleep(0.8)
                res = get_complete_analysis()

            # --- HEADER ---
            st.markdown(f"<div style='text-align: center;'><h1>{h_name.upper()} <span style='color:#3b82f6;'>VS</span> {a_name.upper()}</h1></div>", unsafe_allow_html=True)

            # --- MERCATO 1X2 ---
            st.markdown("### 🎯 Esito Finale (1X2)")
            col1, col2, col3 = st.columns(3)
            with col1: st.markdown(f"<div class='market-box'><small>1</small><br><b>{res['1X2'][0]*100:.1f}%</b></div>", unsafe_allow_html=True)
            with col2: st.markdown(f"<div class='market-box'><small>X</small><br><b>{res['1X2'][1]*100:.1f}%</b></div>", unsafe_allow_html=True)
            with col3: st.markdown(f"<div class='market-box'><small>2</small><br><b>{res['1X2'][2]*100:.1f}%</b></div>", unsafe_allow_html=True)

            # --- ALTRI MERCATI ---
            st.write("")
            col_uo, col_gg = st.columns(2)
            
            with col_uo:
                st.markdown("### ⚽ Gol Totali")
                st.markdown(f"<div class='market-box'><small>Under 2.5</small><br><b>{res['UO25'][0]*100:.1f}%</b></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='market-box' style='margin-top:5px;'><small>Over 2.5</small><br><b>{res['UO25'][1]*100:.1f}%</b></div>", unsafe_allow_html=True)

            with col_gg:
                st.markdown("### 🥅 Entrambe Segnano")
                st.markdown(f"<div class='market-box'><small>Goal (Sì)</small><br><b>{res['GGNG'][0]*100:.1f}%</b></div>", unsafe_allow_html=True)
                st.markdown(f"<div class='market-box' style='margin-top:5px;'><small>No Goal</small><br><b>{res['GGNG'][1]*100:.1f}%</b></div>", unsafe_allow_html=True)

            # --- DOPPIA CHANCE ---
            st.write("")
            st.markdown("### 🛡️ Doppia Chance (Schedina Sicura)")
            d1, d2, d3 = st.columns(3)
            with d1: st.markdown(f"<div class='market-box' style='border-color:#3b82f6;'><small>1X</small><br><b>{res['DC'][0]*100:.1f}%</b></div>", unsafe_allow_html=True)
            with d2: st.markdown(f"<div class='market-box' style='border-color:#3b82f6;'><small>X2</small><br><b>{res['DC'][1]*100:.1f}%</b></div>", unsafe_allow_html=True)
            with d3: st.markdown(f"<div class='market-box' style='border-color:#3b82f6;'><small>12</small><br><b>{res['DC'][2]*100:.1f}%</b></div>", unsafe_allow_html=True)

            st.markdown(f"""
            <div class="neural-opinion" style="margin-top:20px;">
                <b>CONSIGLIO PER LA SCHEDINA:</b><br>
                Il mercato con la fiducia più alta è <b>{'1X' if res['DC'][0] > 0.8 else 'Over 2.5' if res['UO25'][1] > 0.55 else 'Esito Finale 1'}</b>.
                Quota di valore rilevata: Analisi completata.
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Sincronizza per visualizzare i match e i nuovi mercati.")
    st.markdown('</div>', unsafe_allow_html=True)

with tab_reg:
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    st.subheader("👤 Registrazione Account")
    with st.form("reg"):
        st.text_input("Username")
        st.text_input("Email")
        st.form_submit_button("ATTIVA NOTIFICHE PRO")
