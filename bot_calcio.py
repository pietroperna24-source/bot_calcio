import streamlit as st
import time
import requests
import random
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. CONFIGURAZIONE API ---
API_KEY = "ea1f03fb102749fa9140e20b184f2996" 
BASE_URL = "https://api.football-data.org/v4/"

# --- 2. UI & CSS OTTIMIZZATO ---
st.set_page_config(page_title="AI NEURAL COMMANDER PRO", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden; height: 0px; }
    footer { visibility: hidden; }
    .stApp { background-color: #05070a; color: #e0e0e0; }
    
    @media (max-width: 768px) {
        [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
    }

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
    }

    .market-label { color: #94a3b8; font-size: 0.8rem; text-transform: uppercase; font-weight: bold; }
    .market-val { font-size: 1.2rem; font-weight: 700; color: #3b82f6; }
    
    .score-badge {
        background: #1e293b;
        padding: 5px 12px;
        border-radius: 8px;
        border: 1px solid #3b82f6;
        display: inline-block;
        margin: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGICA DI CALCOLO AVANZATA ---
def get_detailed_analysis():
    # Simulazione di metriche statistiche reali
    p1, px, p2 = random.uniform(0.4, 0.6), random.uniform(0.2, 0.3), random.uniform(0.1, 0.3)
    total = p1 + px + p2
    p1, px, p2 = p1/total, px/total, p2/total
    
    return {
        "win_probs": [p1, px, p2],
        "uo25": [random.uniform(0.4, 0.6), random.uniform(0.4, 0.6)],
        "power_index": {"home": random.randint(75, 98), "away": random.randint(65, 92)},
        "exact_scores": [("2-1", "14%"), ("1-0", "12%"), ("1-1", "10%")],
        "tactical_note": random.choice([
            "Alta pressione offensiva prevista per i padroni di casa.",
            "Squadra ospite focalizzata su contropiedi rapidi.",
            "Match equilibrato a centrocampo, attesi pochi spazi.",
            "Difesa ospite vulnerabile sui calci piazzati."
        ])
    }

def fetch_matches(league_code):
    headers = {'X-Auth-Token': API_KEY}
    url = f"{BASE_URL}competitions/{league_code}/matches?status=SCHEDULED"
    try:
        res = requests.get(url, headers=headers, timeout=10)
        return res.json().get('matches', [])
    except: return []

def format_time(iso_date):
    dt = datetime.fromisoformat(iso_date.replace('Z', '+00:00')) + timedelta(hours=2)
    return dt.strftime("%H:%M")

# --- 4. MAIN APP ---
st.title("🛡️ AI NEURAL COMMANDER v9.0")

# Selettore Campionato
st.markdown('<div class="data-card">', unsafe_allow_html=True)
c1, c2 = st.columns([1, 2])
with c1:
    league = st.selectbox("🏆 Campionato", ["Serie A (SA)", "Premier League (PL)", "La Liga (PD)"])
    l_code = league.split("(")[1].replace(")", "")
with c2:
    if st.button("🔄 SINCRONIZZA EVENTI LIVE", use_container_width=True):
        st.session_state.matches = fetch_matches(l_code)

matches = st.session_state.get('matches', [])

if matches:
    labels = [f"{format_time(m['utcDate'])} | {m['homeTeam']['name']} vs {m['awayTeam']['name']}" for m in matches]
    selected = st.selectbox("🔍 Seleziona Match per Intelligence Report:", ["--- Seleziona ---"] + labels)

    if selected != "--- Seleziona ---":
        m_data = matches[labels.index(selected)]
        h_name, a_name = m_data['homeTeam']['name'], m_data['awayTeam']['name']
        
        with st.status("🧬 Estrazione Dati Neurali...", expanded=True) as s:
            time.sleep(0.7)
            data = get_detailed_analysis()
            s.update(label="Analisi Completata!", state="complete")

        # --- REPORT DETTAGLIATO ---
        st.markdown(f"<div style='text-align:center;'><h1>{h_name.upper()} vs {a_name.upper()}</h1></div>", unsafe_allow_html=True)
        
        col_main, col_side = st.columns([2, 1])

        with col_main:
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            st.subheader("📊 Analisi Probabilistica")
            
            # Grafico 1X2
            fig = go.Figure(go.Bar(
                x=['1', 'X', '2'], 
                y=[data['win_probs'][0]*100, data['win_probs'][1]*100, data['win_probs'][2]*100],
                marker_color=['#3b82f6', '#1e293b', '#ef4444']
            ))
            fig.update_layout(height=250, margin=dict(t=10,b=10,l=10,r=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
            st.plotly_chart(fig, use_container_width=True)
            
            # Dettagli Tecnici
            st.markdown(f"""
            <div class="neural-box">
                <b>🤖 AI INSIGHT:</b><br>
                {data['tactical_note']}<br><br>
                <b>FORMA TEAM:</b><br>
                {h_name}: {data['power_index']['home']}% | {a_name}: {data['power_index']['away']}%
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_side:
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            st.subheader("🎯 Pronostici Extra")
            
            # Risultati Esatti
            st.write("**Risultati Esatti Probabili:**")
            for score, prob in data['exact_scores']:
                st.markdown(f"<div class='score-badge'>{score} <small>({prob})</small></div>", unsafe_allow_html=True)
            
            st.divider()
            
            # Mercati Veloci
            st.markdown(f"<span class='market-label'>Under 2.5:</span> <span class='market-val'>{data['uo25'][0]*100:.0f}%</span>", unsafe_allow_html=True)
            st.markdown(f"<br><span class='market-label'>Over 2.5:</span> <span class='market-val'>{data['uo25'][1]*100:.0f}%</span>", unsafe_allow_html=True)
            
            st.divider()
            
            # Quota Suggerita
            fair_odd = 1/data['win_probs'][0] if data['win_probs'][0] > data['win_probs'][2] else 1/data['win_probs'][2]
            st.success(f"💎 Value Bet: **{fair_odd:.2f}**")
            st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("Sincronizza per visualizzare i match e i dettagli dell'IA.")
st.markdown('</div>', unsafe_allow_html=True)
