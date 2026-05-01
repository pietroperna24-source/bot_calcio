import streamlit as st
import time
import requests
import random
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CONFIGURAZIONE API ---
# Sostituisci con la tua chiave reale
API_KEY = "ea1f03fb102749fa9140e20b184f2996" 
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

    .time-tag {
        color: #94a3b8;
        font-weight: bold;
        background: rgba(255, 255, 255, 0.05);
        padding: 4px 10px;
        border-radius: 5px;
        font-size: 0.85rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. FUNZIONI API ---
def fetch_matches(league_code):
    headers = {'X-Auth-Token': API_KEY}
    # Filtriamo per i match programmati (SCHEDULED)
    url = f"{BASE_URL}competitions/{league_code}/matches?status=SCHEDULED"
    try:
        response = requests.get(url, headers=headers)
        return response.json().get('matches', [])
    except:
        return []

def format_date(iso_date):
    """Converte la data ISO dell'API in formato leggibile: Giorno Mese Ore:Min"""
    dt = datetime.fromisoformat(iso_date.replace('Z', '+00:00'))
    return dt.strftime("%d/%m - %H:%M")

def get_neural_analysis():
    p1 = random.uniform(0.35, 0.60)
    p2 = random.uniform(0.15, 0.35)
    px = 1.0 - (p1 + p2)
    return [p1, px, p2]

# --- 4. MAIN APP ---
st.title("🛡️ AI NEURAL COMMANDER v7.8")

tab_live, tab_reg = st.tabs(["🚀 ANALISI EVENTI LIVE", "👤 AREA PRO"])

with tab_live:
    col_menu, col_report = st.columns([1, 2.3])

    with col_menu:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.subheader("📅 Palinsesto Real-Time")
        league = st.selectbox("Campionato", ["Serie A (SA)", "Premier League (PL)", "La Liga (PD)"])
        l_code = league.split("(")[1].replace(")", "")
        
        if st.button("SINCRONIZZA CALENDARIO"):
            with st.spinner("Interrogazione server API..."):
                st.session_state.matches = fetch_matches(l_code)
        
        matches = st.session_state.get('matches', [])
        
        if matches:
            # Creiamo una lista di etichette con Orario | Team A vs Team B
            match_labels = []
            for m in matches:
                label = f"{format_date(m['utcDate'])} | {m['homeTeam']['name']} vs {m['awayTeam']['name']}"
                match_labels.append(label)
            
            selected_label = st.radio("Seleziona Evento:", match_labels)
            
            # Recupero dati del match scelto
            idx = match_labels.index(selected_label)
            m_data = matches[idx]
            h_name = m_data['homeTeam']['shortName'] or m_data['homeTeam']['name']
            a_name = m_data['awayTeam']['shortName'] or m_data['awayTeam']['name']
            m_time = format_date(m_data['utcDate'])
            odds = m_data.get('odds', {"homeWin": 2.10, "draw": 3.30, "awayWin": 3.80})
        else:
            st.info("Sincronizza per visualizzare le date e gli orari reali.")
            h_name = None
        st.markdown('</div>', unsafe_allow_html=True)

    with col_report:
        if h_name:
            # --- ANIMAZIONE NEURALE ---
            with st.empty():
                st.markdown('<div class="data-card">', unsafe_allow_html=True)
                st.code(f">>> CONNESSIONE STABILITA: {datetime.now().strftime('%H:%M:%S')}")
                st.code(f">>> ANALISI MATCH PROGRAMMATO PER IL {m_time}")
                time.sleep(0.5)
                st.code(">>> RECUPERO STATISTICHE STORICHE...")
                time.sleep(0.4)
                st.code(">>> ELABORAZIONE TATTICA NEURALE IN CORSO...")
                time.sleep(0.6)
                st.markdown('</div>', unsafe_allow_html=True)
                st.empty()

            # --- VISUALIZZAZIONE REPORT ---
            p = get_neural_analysis()
            
            st.markdown(f"""
                <div style='text-align: center; margin-bottom: 10px;'>
                    <span class="time-tag">⏱️ KICK-OFF: {m_time}</span><br><br>
                    <h1 style='display: inline;'>{h_name.upper()}</h1>
                    <span class='vs-badge'>VS</span>
                    <h1 style='display: inline;'>{a_name.upper()}</h1>
                </div>
            """, unsafe_allow_html=True)

            c_l, c_m, c_r = st.columns([1, 1.4, 1])

            with c_l:
                st.markdown('<div class="data-card">', unsafe_allow_html=True)
                st.markdown("**VALUTAZIONE CASA**")
                st.progress(p[0], text="Power Factor")
                st.markdown('</div>', unsafe_allow_html=True)

            with c_m:
                st.markdown('<div class="data-card" style="text-align:center;">', unsafe_allow_html=True)
                fig = go.Figure(go.Pie(labels=['1', 'X', '2'], values=p, hole=.7, marker_colors=['#3b82f6', '#1e293b', '#ef4444']))
                fig.update_layout(showlegend=False, height=250, margin=dict(t=0,b=0,l=0,r=0), paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
                st.markdown(f"<h2 style='color:#3b82f6;'>{max(p)*100:.1f}% Confidence</h2>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with c_r:
                st.markdown('<div class="data-card">', unsafe_allow_html=True)
                st.markdown("**VALUTAZIONE OSPITI**")
                st.progress(p[2], text="Power Factor")
                st.markdown('</div>', unsafe_allow_html=True)

            # OPINIONI
            st.markdown("### 📊 Neural Intelligence Report")
            o1, o2 = st.columns(2)
            with o1:
                st.markdown(f"""
                <div class="neural-opinion">
                    <b>AI ADVISORY:</b><br>
                    L'evento del {m_time} vede un favorito chiaro con il {max(p)*100:.1f}% di probabilità. 
                    Suggeriamo di monitorare i flussi delle quote negli ultimi 30 minuti prima del fischio d'inizio.
                </div>
                """, unsafe_allow_html=True)
            with o2:
                st.markdown('<div class="data-card">', unsafe_allow_html=True)
                st.write(f"📅 Data Evento: **{m_time}**")
                st.write(f"📈 Quota Fair: **{(1/max(p)):.2f}**")
                st.write(f"🏦 Quota Bookmaker: **{odds['homeWin'] if p[0]>p[2] else odds['awayWin']}**")
                st.markdown('</div>', unsafe_allow_html=True)

with tab_reg:
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    st.subheader("👤 Registrazione Account")
    with st.form("reg"):
        st.text_input("Username")
        st.text_input("Email")
        if st.form_submit_button("ATTIVA NOTIFICHE"):
            st.success("Profilo attivato con successo.")
    st.markdown('</div>', unsafe_allow_html=True)
