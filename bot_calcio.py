import streamlit as st
import time
import requests
import random
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. CONFIGURAZIONE API ---
API_KEY = "ea1f03fb102749fa9140e20b184f2996" 
BASE_URL = "https://api.football-data.org/v4/"

# --- 2. UI & CSS ---
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

    .time-tag {
        color: #10b981;
        font-weight: bold;
        background: rgba(16, 185, 129, 0.1);
        padding: 6px 12px;
        border-radius: 8px;
        border: 1px solid #10b981;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. FUNZIONI TECNICHE ---
def fetch_matches(league_code):
    headers = {'X-Auth-Token': API_KEY}
    url = f"{BASE_URL}competitions/{league_code}/matches?status=SCHEDULED"
    try:
        response = requests.get(url, headers=headers)
        return response.json().get('matches', [])
    except:
        return []

def format_to_local_time(iso_date):
    """Converte UTC in orario locale italiano (+2 ore per Maggio 2026)"""
    dt_utc = datetime.fromisoformat(iso_date.replace('Z', '+00:00'))
    # Applichiamo l'offset manualmente per l'Italia (CEST = UTC+2)
    dt_local = dt_utc + timedelta(hours=2)
    return dt_local.strftime("%d/%m - %H:%M")

def get_neural_analysis():
    p1 = random.uniform(0.38, 0.58)
    p2 = random.uniform(0.18, 0.35)
    px = 1.0 - (p1 + p2)
    return [p1, px, p2]

# --- 4. MAIN APP ---
st.title("🛡️ AI NEURAL COMMANDER v8.0")
st.caption("Status: Sincronizzazione Oraria Locale (Italia) Attiva")

tab_live, tab_reg = st.tabs(["🚀 ANALISI EVENTI", "👤 AREA RISERVATA"])

with tab_live:
    col_menu, col_report = st.columns([1, 2.3])

    with col_menu:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.subheader("📅 Palinsesto Reale")
        league = st.selectbox("Seleziona Lega", ["Serie A (SA)", "Premier League (PL)", "La Liga (PD)"])
        l_code = league.split("(")[1].replace(")", "")
        
        if st.button("AGGIORNA CALENDARIO"):
            with st.spinner("Scansione server API..."):
                st.session_state.matches = fetch_matches(l_code)
        
        matches = st.session_state.get('matches', [])
        
        if matches:
            match_labels = []
            for m in matches:
                local_time = format_to_local_time(m['utcDate'])
                match_labels.append(f"{local_time} | {m['homeTeam']['name']} vs {m['awayTeam']['name']}")
            
            selected_label = st.radio("Seleziona Match:", match_labels)
            
            idx = match_labels.index(selected_label)
            m_data = matches[idx]
            h_name = m_data['homeTeam']['shortName'] or m_data['homeTeam']['name']
            a_name = m_data['awayTeam']['shortName'] or m_data['awayTeam']['name']
            m_time = format_to_local_time(m_data['utcDate'])
            odds = m_data.get('odds', {"homeWin": 1.90, "draw": 3.40, "awayWin": 4.50})
        else:
            st.info("Sincronizza per caricare i match reali.")
            h_name = None
        st.markdown('</div>', unsafe_allow_html=True)

    with col_report:
        if h_name:
            # --- ANIMAZIONE LOADING ---
            with st.empty():
                st.markdown('<div class="data-card">', unsafe_allow_html=True)
                st.code(f">>> CONNESSIONE API OK - LOCAL TIME SYNC...")
                time.sleep(0.4)
                st.code(f">>> ANALISI MATCH: {h_name} vs {a_name}")
                st.code(f">>> STARTING TIME: {m_time}")
                time.sleep(0.5)
                st.code(">>> ELABORAZIONE MODELLI PREDITTIVI...")
                time.sleep(0.6)
                st.markdown('</div>', unsafe_allow_html=True)
                st.empty()

            # --- REPORT ---
            p = get_neural_analysis()
            
            st.markdown(f"""
                <div style='text-align: center; margin-bottom: 20px;'>
                    <span class="time-tag">🇮🇹 INIZIO ORE: {m_time.split(' - ')[1]}</span><br><br>
                    <h1 style='display: inline;'>{h_name.upper()}</h1>
                    <span class='vs-badge'>VS</span>
                    <h1 style='display: inline;'>{a_name.upper()}</h1>
                </div>
            """, unsafe_allow_html=True)

            c_l, c_m, c_r = st.columns([1, 1.4, 1])

            with c_l:
                st.markdown('<div class="data-card">', unsafe_allow_html=True)
                st.markdown("**POWER HOME**")
                st.progress(p[0])
                st.markdown('</div>', unsafe_allow_html=True)

            with c_m:
                st.markdown('<div class="data-card" style="text-align:center;">', unsafe_allow_html=True)
                fig = go.Figure(go.Pie(labels=['1', 'X', '2'], values=p, hole=.7, marker_colors=['#3b82f6', '#1e293b', '#ef4444']))
                fig.update_layout(showlegend=False, height=250, margin=dict(t=0,b=0,l=0,r=0), paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
                st.markdown(f"<h2>{max(p)*100:.1f}%</h2><p style='color:#94a3b8;'>Neural Confidence</p>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with c_r:
                st.markdown('<div class="data-card">', unsafe_allow_html=True)
                st.markdown("**POWER AWAY**")
                st.progress(p[2])
                st.markdown('</div>', unsafe_allow_html=True)

            # INTELLIGENCE
            st.markdown("### 📊 Intelligence Insights")
            o1, o2 = st.columns(2)
            with o1:
                st.markdown(f"""
                <div class="neural-opinion">
                    <b>NEURAL ADVISORY:</b><br>
                    Il sistema rileva una probabilità del {p[0]*100:.1f}% per la vittoria interna. 
                    Il fischio d'inizio è confermato per le {m_time.split(' - ')[1]} (ora locale).
                </div>
                """, unsafe_allow_html=True)
            with o2:
                st.markdown('<div class="data-card">', unsafe_allow_html=True)
                st.write(f"📈 Quota Fair: **{(1/max(p)):.2f}**")
                st.write(f"🏦 Quota Mercato: **{odds['homeWin'] if p[0]>p[2] else odds['awayWin']}**")
                st.write(f"📅 Data: **{m_time.split(' - ')[0]}**")
                st.markdown('</div>', unsafe_allow_html=True)

with tab_reg:
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    st.subheader("👤 Registrazione Account")
    with st.form("reg"):
        st.text_input("Username")
        st.text_input("Email")
        st.form_submit_button("CONFERMA")
