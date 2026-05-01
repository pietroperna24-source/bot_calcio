import streamlit as st
import requests
import sqlite3
import hashlib
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CONFIGURAZIONE ---
st.set_page_config(page_title="NEURAL BET AI - RAPID", page_icon="🏆", layout="wide")

def init_db():
    conn = sqlite3.connect('neural_bet_pro.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, created_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS favorites (user TEXT, match_name TEXT, prediction TEXT, odds TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

def hash_pwd(pwd):
    return hashlib.sha256(str.encode(pwd)).hexdigest()

init_db()

# --- 2. MOTORE AI ---
class NeuralEngine:
    @staticmethod
    def analyze_market(o1, ox, o2):
        margin = (1/o1) + (1/ox) + (1/o2)
        p1, px, p2 = (1/o1)/margin, (1/ox)/margin, (1/o2)/margin
        return {"p1": p1, "px": px, "p2": p2, "fair_1": 1/p1}

    @staticmethod
    def get_verdict(p1, o1):
        valore = (o1 * p1) - 1
        if valore > 0.05: return f"🔥 VALORE: +{valore:.1%}", "#00ff00"
        return ("✅ ALTA PROBABILITÀ", "#88ccff") if p1 > 0.60 else ("⚠️ RISCHIO", "#ffaa00")

# --- 3. CSS "DEEP CLEAN" ---
st.markdown("""
    <style>
    #MainMenu, header, footer {visibility: hidden; display: none !important;}
    .stAppDeployButton, button[title="Manage app"], [data-testid="stStatusWidget"] {display: none !important;}
    .stApp { background: #0e1117; }
    .main-card { background: #161b22; border-radius: 15px; padding: 20px; border: 1px solid #30363d; margin-bottom: 20px;}
    .block-container {padding-top: 1rem;}
    </style>
    """, unsafe_allow_html=True)

# --- 4. LOGIN ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    cols = st.columns([1, 1.5, 1])
    with cols[1]:
        st.title("🧠 Neural Engine")
        t1, t2 = st.tabs(["Accedi", "Registrati"])
        with t1:
            u, p = st.text_input("User"), st.text_input("Pass", type="password")
            if st.button("LOG IN"):
                conn = sqlite3.connect('neural_bet_pro.db')
                res = conn.execute('SELECT password FROM users WHERE username=?', (u,)).fetchone()
                conn.close()
                if res and res[0] == hash_pwd(p):
                    st.session_state.logged_in, st.session_state.user = True, u
                    st.rerun()
        with t2:
            nu, np = st.text_input("Nuovo User"), st.text_input("Nuova Pass", type="password")
            if st.button("CREA ACCOUNT"):
                try:
                    conn = sqlite3.connect('neural_bet_pro.db')
                    conn.execute('INSERT INTO users VALUES (?,?,?)', (nu, hash_pwd(np), datetime.now().isoformat()))
                    conn.commit()
                    conn.close()
                    st.success("Registrato!")
                except: st.error("Errore.")

# --- 5. DASHBOARD OPERATIVA ---
else:
    try:
        RAPID_KEY = st.secrets["RAPID_API_KEY"]
    except:
        st.error("Configura 'RAPID_API_KEY' nei Secrets di Streamlit!")
        RAPID_KEY = None

    with st.sidebar:
        st.title(f"👤 {st.session_state.user}")
        sport_id = st.selectbox("Campionato", [
            ("Serie A", "135"), ("Premier League", "39"), 
            ("La Liga", "140"), ("Bundesliga", "78"), ("Ligue 1", "61")
        ])
        if st.button("Esci"):
            st.session_state.logged_in = False
            st.rerun()

    st.title("🏟️ Analisi Pro - API Football")

    if RAPID_KEY and st.button("🚀 SCANSIONA PARTITE"):
        try:
            url = "https://api-football-v1.p.rapidapi.com/v3/odds"
            # Parametri: prendiamo le quote per la stagione attuale
            querystring = {"league": sport_id[1], "season": "2025", "bookmaker": "6"} 
            headers = {
                "X-RapidAPI-Key": RAPID_KEY,
                "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
            }
            
            response = requests.get(url, headers=headers, params=querystring).json()
            
            matches = response.get('response', [])
            
            if not matches:
                st.info("Nessuna quota disponibile per questa lega al momento.")
            
            for item in matches:
                # Estrazione sicura dei nomi delle squadre dal blocco fixture
                home_team = item['fixture']['timezone'] # Placeholder se fixture name manca
                # In API-Football le quote sono annidate: bookmakers -> bets -> values
                bookmaker = item['bookmakers'][0]
                # Cerchiamo il mercato "Match Winner" (solitamente il primo ID: 1)
                bet = next((b for b in bookmaker['bets'] if b['id'] == 1), None)
                
                if bet:
                    odds_list = bet['values'] # Contiene Home, Draw, Away
                    # Ordine API-Football: [0]=Home, [1]=Draw, [2]=Away
                    o1 = float(odds_list[0]['odd'])
                    ox = float(odds_list[1]['odd'])
                    o2 = float(odds_list[2]['odd'])
                    
                    # Nomi reali delle squadre
                    match_label = f"{item['fixture']['id']}" # ID univoco per il tasto
                    team_h = odds_list[0]['value']
                    team_a = odds_list[2]['value']

                    res = NeuralEngine.analyze_market(o1, ox, o2)
                    verd, color = NeuralEngine.get_verdict(res['p1'], o1)

                    with st.container():
                        st.markdown(f'<div class="main-card"><h3>{team_h} vs {team_a}</h3><b style="color:{color}">{verd}</b></div>', unsafe_allow_html=True)
                        c1, c2 = st.columns(2)
                        with c1:
                            fig = go.Figure(data=[go.Pie(labels=[team_h,'X',team_a], values=[res['p1'],res['px'],res['p2']], hole=.4, marker_colors=['#00ff00','#333','#ff4b4b'])])
                            fig.update_layout(height=200, margin=dict(t=0,b=0,l=0,r=0), showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
                            st.plotly_chart(fig, use_container_width=True)
                        with c2:
                            st.write(f"Quota: **{o1}** | Equa: **{res['fair_1']:.2f}**")
                            if st.button(f"⭐ Salva", key=f"fav_{match_label}"):
                                conn = sqlite3.connect('neural_bet_pro.db')
                                conn.execute('INSERT INTO favorites VALUES (?,?,?,?,?)', 
                                            (st.session_state.user, f"{team_h}-{team_a}", verd, str(o1), datetime.now().strftime("%d/%m %H:%M")))
                                conn.commit()
                                conn.close()
                                st.toast("Salvato!")
        except Exception as e:
            st.error(f"Errore tecnico: {e}")
