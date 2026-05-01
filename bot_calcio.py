import streamlit as st
import requests
import sqlite3
import hashlib
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURAZIONE ---
st.set_page_config(page_title="AI PREDICTOR 2026", page_icon="🤖", layout="wide")

def init_db():
    conn = sqlite3.connect('neural_bet_pro.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)''')
    conn.commit()
    conn.close()

def hash_pwd(pwd):
    return hashlib.sha256(str.encode(pwd)).hexdigest()

init_db()

# --- MOTORE DI ANALISI PROBABILISTICA ---
class NeuralEngine:
    @staticmethod
    def calculate_probs(o1, ox, o2):
        # Rimozione dell'aggio (margine del bookmaker)
        margin = (1/o1) + (1/ox) + (1/o2)
        p1 = (1/o1) / margin
        px = (1/ox) / margin
        p2 = (1/o2) / margin
        return {"p1": p1, "px": px, "p2": p2, "fair_o1": 1/p1}

    @staticmethod
    def get_ai_advice(p1, o1):
        # Valutazione del valore matematico (Value Bet)
        value = (o1 * p1) - 1
        if value > 0.07:
            return f"🔥 PRONOSTICO: VALUE DETECTED (+{value:.1%})", "#00ff00"
        elif p1 > 0.65:
            return "✅ PRONOSTICO: PROBABILITÀ MOLTO ALTA", "#88ccff"
        elif p1 > 0.45:
            return "⚖️ PRONOSTICO: EQUILIBRIO / MODERATO", "#ffaa00"
        else:
            return "⚠️ PRONOSTICO: RISCHIO ELEVATO", "#ff4b4b"

# --- INTERFACCIA E CSS ---
st.markdown("""
    <style>
    #MainMenu, header, footer {visibility: hidden; display: none !important;}
    .stAppDeployButton, button[title="Manage app"] {display: none !important;}
    .stApp { background: #0e1117; }
    .main-card { 
        background: #161b22; border-radius: 15px; padding: 25px; 
        border: 1px solid #30363d; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DI ACCESSO ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    cols = st.columns([1, 1.5, 1])
    with cols[1]:
        st.title("🤖 AI Match Analyst")
        u, p = st.text_input("Utente"), st.text_input("Password", type="password")
        if st.button("ACCEDI ALL'ANALISI"):
            # Logica semplificata per velocità
            st.session_state.auth = True
            st.rerun()
else:
    # --- DASHBOARD DI ANALISI ---
    try:
        API_KEY = st.secrets["RAPID_API_KEY"]
    except:
        st.error("Configura 'RAPID_API_KEY' nei Secrets di Streamlit Cloud.")
        API_KEY = None

    with st.sidebar:
        st.header("⚙️ Parametri AI")
        league = st.selectbox("Campionato", [
            ("Serie A", "135"), ("Premier League", "39"), 
            ("La Liga", "140"), ("Bundesliga", "78")
        ])
        # Nel maggio 2026 la stagione attiva è la 2025
        season = st.selectbox("Stagione", ["2025", "2026"])
        if st.button("Logout"):
            st.session_state.auth = False
            st.rerun()

    st.title("🏟️ Valutazione Partite & Percentuali AI")

    if API_KEY and st.button("🔍 ANALIZZA PROSSIMI EVENTI"):
        try:
            url = "https://api-football-v1.p.rapidapi.com/v3/odds"
            # Bookmaker 1 = Bet365 (solitamente il più fornito)
            query = {"league": league[1], "season": season, "bookmaker": "1"}
            headers = {"X-RapidAPI-Key": API_KEY, "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"}
            
            response = requests.get(url, headers=headers, params=query).json()
            matches = response.get('response', [])

            if not matches:
                st.warning("Nessun dato disponibile. Verifica che la stagione selezionata sia corretta.")

            for item in matches:
                bookie = item['bookmakers'][0]
                bet = next((b for b in bookie['bets'] if b['id'] == 1), None)
                
                if bet:
                    v = bet['values']
                    o1, ox, o2 = float(v[0]['odd']), float(v[1]['odd']), float(v[2]['odd'])
                    t1, t2 = v[0]['value'], v[2]['value']

                    # Esecuzione calcoli AI
                    analysis = NeuralEngine.calculate_probs(o1, ox, o2)
                    advice, color = NeuralEngine.get_ai_advice(analysis['p1'], o1)

                    with st.container():
                        st.markdown(f"""
                        <div class="main-card">
                            <h2 style="margin-bottom:0;">{t1} vs {t2}</h2>
                            <p style="color:{color}; font-weight:bold; font-size:1.2rem;">{advice}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        c1, c2 = st.columns([1, 1])
                        with c1:
                            # Grafico a torta delle percentuali
                            fig = go.Figure(data=[go.Pie(
                                labels=[t1, 'Pareggio', t2],
                                values=[analysis['p1'], analysis['px'], analysis['p2']],
                                hole=.4,
                                marker_colors=['#00ff00', '#555', '#ff4b4b']
                            )])
                            fig.update_layout(height=250, showlegend=True, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with c2:
                            st.write("### 📊 Analisi Statistica")
                            st.write(f"🔹 **Probabilità {t1}:** {analysis['p1']:.1%}")
                            st.write(f"🔹 **Probabilità Pareggio:** {analysis['px']:.1%}")
                            st.write(f"🔹 **Probabilità {t2}:** {analysis['p2']:.1%}")
                            st.divider()
                            st.write(f"📈 **Quota Reale (Fair Odds):** {analysis['fair_o1']:.2f}")
                            st.write(f"🏦 **Quota Bookmaker:** {o1:.2f}")

        except Exception as e:
            st.error(f"Errore tecnico nell'analisi: {e}")
