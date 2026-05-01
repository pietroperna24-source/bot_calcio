import streamlit as st
import requests
import sqlite3
import hashlib
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="NEURAL BET AI 2026", page_icon="🏆", layout="wide")

def init_db():
    """Inizializza il database per utenti e salvataggi"""
    conn = sqlite3.connect('neural_bet_pro.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, created_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS favorites 
                 (user TEXT, match_name TEXT, prediction TEXT, odds TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

def hash_pwd(pwd):
    """Criptazione password"""
    return hashlib.sha256(str.encode(pwd)).hexdigest()

init_db()

# --- 2. MOTORE DI CALCOLO AI ---
class NeuralEngine:
    @staticmethod
    def analyze_market(o1, ox, o2):
        """Calcola probabilità reali rimuovendo l'aggio del bookmaker"""
        margin = (1/o1) + (1/ox) + (1/o2)
        p1 = (1/o1) / margin
        px = (1/ox) / margin
        p2 = (1/o2) / margin
        return {
            "p1": p1, "px": px, "p2": p2,
            "fair_1": 1/p1
        }

    @staticmethod
    def get_verdict(p1, o1):
        """Confronta quota reale e quota bookmaker per trovare il valore"""
        valore_casa = (o1 * p1) - 1
        if valore_casa > 0.05:
            return f"🔥 VALORE RILEVATO: +{valore_casa:.1%}", "#00ff00"
        if p1 > 0.60:
            return "✅ ALTA PROBABILITÀ CASA", "#88ccff"
        return "⚠️ RISCHIO / EQUILIBRIO", "#ffaa00"

# --- 3. CSS "DEEP CLEAN" (Rimuove loghi, menu e tasti Streamlit) ---
st.markdown("""
    <style>
    /* Nasconde elementi di sistema */
    #MainMenu, header, footer {visibility: hidden; display: none !important;}
    .stAppDeployButton, button[title="Manage app"], [data-testid="stStatusWidget"] {display: none !important;}
    [data-testid="stCustomComponentToolbar"], [data-testid="stDecoration"] {display: none !important;}
    div[id="viewer-badge"], iframe[title="Manage app"] {display: none !important;}
    
    /* Layout personalizzato */
    .stApp { background: #0e1117; }
    .block-container { padding-top: 1.5rem; }
    .main-card { 
        background: #161b22; 
        border-radius: 15px; 
        padding: 20px; 
        border: 1px solid #30363d; 
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. GESTIONE SESSIONE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

# --- 5. INTERFACCIA ACCESSO ---
if not st.session_state.logged_in:
    cols = st.columns([1, 1.5, 1])
    with cols[1]:
        st.title("🧠 Motore di Analisi Neurale")
        tab1, tab2 = st.tabs(["🔑 Accedi", "📝 Registrati"])
        with tab1:
            u, p = st.text_input("Utente"), st.text_input("Password", type="password")
            if st.button("ENTRA"):
                conn = sqlite3.connect('neural_bet_pro.db')
                res = conn.execute('SELECT password FROM users WHERE username=?', (u,)).fetchone()
                conn.close()
                if res and res[0] == hash_pwd(p):
                    st.session_state.logged_in, st.session_state.user = True, u
                    st.rerun()
                else: st.error("Credenziali errate.")
        with tab2:
            nu, np = st.text_input("Nuovo Utente"), st.text_input("Nuova Password", type="password")
            if st.button("CREA ACCOUNT"):
                try:
                    conn = sqlite3.connect('neural_bet_pro.db')
                    conn.execute('INSERT INTO users VALUES (?,?,?)', (nu, hash_pwd(np), datetime.now().isoformat()))
                    conn.commit()
                    conn.close()
                    st.success("Account creato! Effettua il login.")
                except: st.error("Errore: Utente già esistente.")

# --- 6. DASHBOARD OPERATIVA ---
else:
    # Recupero Chiave dai Secrets di Streamlit Cloud
    try:
        RAPID_KEY = st.secrets["RAPID_API_KEY"]
    except:
        st.error("ERRORE: Inserisci 'RAPID_API_KEY' nei Secrets di Streamlit Cloud!")
        RAPID_KEY = None

    with st.sidebar:
        st.title(f"👤 {st.session_state.user}")
        sport_id = st.selectbox("Campionato", [
            ("Serie A", "135"), ("Premier League", "39"), 
            ("La Liga", "140"), ("Bundesliga", "78")
        ])
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    st.title("🏟️ Analisi Strategica 2026")

    if RAPID_KEY and st.button("🚀 AVVIA SCANSIONE"):
        try:
            url = "https://api-football-v1.p.rapidapi.com/v3/odds"
            # ANNO 2026 E BOOKMAKER 1 (BET365)
            querystring = {"league": sport_id[1], "season": "2025", "bookmaker": "1"} 
            headers = {
                "X-RapidAPI-Key": RAPID_KEY,
                "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
            }
            
            response = requests.get(url, headers=headers, params=querystring).json()
            matches = response.get('response', [])
            
            if not matches:
                st.warning("Nessuna quota disponibile per il 2026 su questa lega al momento.")
            
            for item in matches:
                if not item['bookmakers']: continue
                
                # Cerchiamo il mercato Match Winner (id: 1)
                bm = item['bookmakers'][0]
                bet = next((b for b in bm['bets'] if b['id'] == 1), None)
                
                if bet and len(bet['values']) >= 3:
                    v = bet['values']
                    o1, ox, o2 = float(v[0]['odd']), float(v[1]['odd']), float(v[2]['odd'])
                    t_h, t_a = v[0]['value'], v[2]['value']

                    res = NeuralEngine.analyze_market(o1, ox, o2)
                    verd, color = NeuralEngine.get_verdict(res['p1'], o1)

                    with st.container():
                        st.markdown(f'<div class="main-card"><h3>{t_h} vs {t_a}</h3><b style="color:{color}">{verd}</b></div>', unsafe_allow_html=True)
                        c1, c2 = st.columns(2)
                        with c1:
                            fig = go.Figure(data=[go.Pie(labels=[t_h,'X',t_a], values=[res['p1'],res['px'],res['p2']], hole=.4, marker_colors=['#00ff00','#333','#ff4b4b'])])
                            fig.update_layout(height=200, margin=dict(t=0,b=0,l=0,r=0), showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
                            st.plotly_chart(fig, use_container_width=True)
                        with c2:
                            st.write(f"Quota: **{o1}** | Fair: **{res['fair_1']:.2f}**")
                            if st.button(f"Salva", key=f"save_{item['fixture']['id']}"):
                                conn = sqlite3.connect('neural_bet_pro.db')
                                conn.execute('INSERT INTO favorites VALUES (?,?,?,?,?)', 
                                            (st.session_state.user, f"{t_h}-{t_a}", verd, str(o1), datetime.now().strftime("%d/%m %H:%M")))
                                conn.commit()
                                conn.close()
                                st.toast("Salvato!")
        except Exception as e:
            st.error(f"Errore tecnico API: {e}")
