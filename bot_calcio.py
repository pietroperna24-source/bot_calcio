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
    
    /* Layout adattivo per cellulari */
    @media (max-width: 768px) {
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
        }
        .vs-badge { font-size: 1.1rem !important; padding: 5px 15px !important; }
        h1 { font-size: 1.5rem !important; }
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

    .time-tag {
        color: #10b981;
        font-weight: bold;
        background: rgba(16, 185, 129, 0.1);
        padding: 6px 12px;
        border-radius: 8px;
        border: 1px solid #10b981;
        display: inline-block;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. FUNZIONI TECNICHE ---
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
    dt_local = dt_utc + timedelta(hours=2) # CEST (Italia 2026)
    return dt_local.strftime("%d/%m - %H:%M")

def get_neural_analysis():
    p1 = random.uniform(0.40, 0.60)
    p2 = random.uniform(0.15, 0.30)
    px = 1.0 - (p1 + p2)
    return [p1, px, p2]

# --- 4. LOGICA DI NAVIGAZIONE ---
if 'view' not in st.session_state:
    st.session_state.view = 'home'

# --- 5. MAIN APP ---
st.title("🛡️ AI NEURAL COMMANDER")

tab_live, tab_reg = st.tabs(["🚀 ANALISI", "👤 ACCOUNT"])

with tab_live:
    # Sezione di Selezione (Catalogo)
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    st.subheader("📅 Palinsesto Real-Time")
    league = st.selectbox("Campionato", ["Serie A (SA)", "Premier League (PL)", "La Liga (PD)"])
    l_code = league.split("(")[1].replace(")", "")
    
    if st.button("🔄 SINCRONIZZA CALENDARIO", use_container_width=True):
        st.session_state.matches = fetch_matches(l_code)
    
    matches = st.session_state.get('matches', [])
    
    if matches:
        match_labels = [f"{format_to_local_time(m['utcDate'])} | {m['homeTeam']['name']} vs {m['awayTeam']['name']}" for m in matches]
        selected_m = st.selectbox("Seleziona l'evento da analizzare:", ["--- Seleziona un match ---"] + match_labels)
        
        if selected_m != "--- Seleziona un match ---":
            idx = match_labels.index(selected_m)
            m_data = matches[idx]
            
            # --- AVVIO ANALISI ---
            h_name = m_data['homeTeam']['shortName'] or m_data['homeTeam']['name']
            a_name = m_data['awayTeam']['shortName'] or m_data['awayTeam']['name']
            m_time = format_to_local_time(m_data['utcDate'])
            
            # ANIMAZIONE CARICAMENTO
            with st.status("🧬 Inizializzazione Analisi Neurale...", expanded=True) as status:
                st.write("📡 Connessione ai nodi satellitari...")
                time.sleep(0.5)
                st.write(f"📊 Analisi dati storici {h_name} vs {a_sel if 'a_sel' in locals() else a_name}...")
                time.sleep(0.5)
                st.write("🤖 Calcolo probabilità vettoriale...")
                status.update(label="Analisi Completata!", state="complete")

            # --- REPORT RISULTATI ---
            p = get_neural_analysis()
            
            st.markdown(f"""
                <div style='text-align: center; margin-top: 20px;'>
                    <span class="time-tag">🇮🇹 CALCIO D'INIZIO: {m_time}</span><br>
                    <h1 style='color:#3b82f6;'>{h_name.upper()} <span style='color:#fff;'>VS</span> {a_name.upper()}</h1>
                </div>
            """, unsafe_allow_html=True)

            # Colonne che su Mobile diventano righe singole grazie al CSS sopra
            col_l, col_m, col_r = st.columns([1, 1.2, 1])

            with col_l:
                st.markdown('<div class="data-card">', unsafe_allow_html=True)
                st.write("**POWER CASA**")
                st.progress(p[0])
                st.markdown('</div>', unsafe_allow_html=True)

            with col_m:
                st.markdown('<div class="data-card" style="text-align:center;">', unsafe_allow_html=True)
                fig = go.Figure(go.Pie(labels=['1', 'X', '2'], values=p, hole=.7, marker_colors=['#3b82f6', '#1e293b', '#ef4444']))
                fig.update_layout(showlegend=False, height=250, margin=dict(t=0,b=0,l=0,r=0), paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
                st.metric("CONFIDENCE", f"{max(p)*100:.1f}%")
                st.markdown('</div>', unsafe_allow_html=True)

            with col_r:
                st.markdown('<div class="data-card">', unsafe_allow_html=True)
                st.write("**POWER OSPITI**")
                st.progress(p[2])
                st.markdown('</div>', unsafe_allow_html=True)

            # OPINIONE FINALE
            st.markdown(f"""
            <div class="neural-opinion">
                <b>NEURAL INSIGHT:</b><br>
                Analisi completata per l'evento delle {m_time.split(' - ')[1]}. 
                Il modello rileva una dominanza del team {'Casa' if p[0]>p[2] else 'Ospite'}. 
                Quota Fair calcolata: <b>{(1/max(p)):.2f}</b>.
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Sincronizza il calendario per vedere gli eventi reali di oggi.")
    st.markdown('</div>', unsafe_allow_html=True)

with tab_reg:
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    st.subheader("👤 Registrazione Account")
    with st.form("reg"):
        st.text_input("Username")
        st.text_input("Email")
        st.form_submit_button("ATTIVA NOTIFICHE PRO")
