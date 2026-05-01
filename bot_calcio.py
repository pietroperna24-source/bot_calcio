import streamlit as st
import requests
import sqlite3
import hashlib
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="PIATTAFORMA NEURALE AI", page_icon="🏆", layout="wide")

def init_db():
    """Inizializza il database SQLite per utenti e preferiti"""
    conn = sqlite3.connect('neural_bet_pro.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, created_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS favorites 
                 (user TEXT, match_name TEXT, prediction TEXT, odds TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

def hash_pwd(pwd):
    """Cripta la password per la sicurezza"""
    return hashlib.sha256(str.encode(pwd)).hexdigest()

init_db()

# --- 2. MOTORE DI CALCOLO AI ---
class NeuralEngine:
    @staticmethod
    def analyze_market(o1, ox, o2):
        """Rimuove l'aggio del bookmaker e calcola la probabilità reale"""
        margin = (1/o1) + (1/ox) + (1/o2)
        p1 = (1/o1) / margin
        px = (1/ox) / margin
        p2 = (1/o2) / margin
        return {
            "p1": p1, "px": px, "p2": p2,
            "margin": margin - 1,
            "fair_1": 1/p1
        }

    @staticmethod
    def get_verdict(p1, o1):
        """Determina il consiglio basato sul valore matematico"""
        valore_casa = (o1 * p1) - 1
        if valore_casa > 0.05:
            return f"🔥 VALORE RILEVATO: +{valore_casa:.1%}", "#00ff00"
        if p1 > 0.60:
            return "✅ ALTA PROBABILITÀ CASA", "#88ccff"
        return "⚠️ RISCHIO / EQUILIBRIO", "#ffaa00"

# --- 3. CSS "STEALTH MODE" (RIMOZIONE TOTALE ELEMENTI ADMIN) ---
st.markdown("""
    <style>
    /* Nasconde menu, header e footer di sistema */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Nasconde il tasto 'Manage app' e 'Deploy' di Streamlit Cloud */
    .stAppDeployButton {display: none !important;}
    button[title="Manage app"] {display: none !important;}
    [data-testid="stCustomComponentToolbar"] {display: none !important;}
    
    /* Nasconde il menu di debug in basso a destra */
    #viewer-badge {display: none !important;}

    /* Riduce lo spazio bianco in alto dopo la rimozione dell'header */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1rem;
    }

    .stApp { background: #0e1117; }
    
    .main-card { 
        background: #161b22; 
        border-radius: 15px; 
        padding: 20px; 
        border: 1px solid #30363d; 
        margin-bottom: 20px;
    }
    
    .fav-card {
        background: #1c2128;
        padding: 15px;
        border-left: 5px solid #58a6ff;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. GESTIONE SESSIONE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

# --- 5. INTERFACCIA: ACCESSO E REGISTRAZIONE ---
if not st.session_state.logged_in:
    cols = st.columns([1, 1.5, 1])
    with cols[1]:
        st.title("🧠 Motore di Analisi Neurale")
        st.write("Accedi alla piattaforma di intelligenza artificiale per il calcio.")
        tab1, tab2 = st.tabs(["🔑 Entra", "📝 Registrati"])
        
        with tab1:
            u = st.text_input("Nome Utente")
            p = st.text_input("Password", type="password")
            if st.button("ACCEDI"):
                conn = sqlite3.connect('neural_bet_pro.db')
                res = conn.execute('SELECT password FROM users WHERE username=?', (u,)).fetchone()
                conn.close()
                if res and res[0] == hash_pwd(p):
                    st.session_state.logged_in, st.session_state.user = True, u
                    st.rerun()
                else: st.error("Credenziali non corrette.")
        
        with tab2:
            nu = st.text_input("Scegli Nome Utente")
            np = st.text_input("Scegli Password", type="password")
            if st.button("CREA ACCOUNT"):
                try:
                    conn = sqlite3.connect('neural_bet_pro.db')
                    conn.execute('INSERT INTO users VALUES (?,?,?)', (nu, hash_pwd(np), datetime.now().strftime("%Y-%m-%d %H:%M")))
                    conn.commit()
                    conn.close()
                    st.success("Account creato! Ora puoi effettuare l'accesso.")
                except: st.error("Nome utente già esistente.")

# --- 6. INTERFACCIA: DASHBOARD UTENTE ---
else:
    with st.sidebar:
        st.title(f"👤 {st.session_state.user}")
        st.write("Stato: **Utente Verificato**")
        st.divider()
        api_key = st.text_input("Chiave API Personale", type="password")
        sport = st.selectbox("Campionato", [
            ("Serie A", "soccer_italy_serie_a"),
            ("Premier League", "soccer_epl"),
            ("La Liga", "soccer_spain_la_liga"),
            ("Bundesliga", "soccer_germany_bundesliga")
        ])
        st.divider()
        if st.button("Esci dal Sistema"):
            st.session_state.logged_in = False
            st.rerun()

    st.title("🏟️ Dashboard Strategia AI")
    tab_scan, tab_favs = st.tabs(["🔍 Analisi Mercati", "⭐ Preferiti"])

    with tab_scan:
        if st.button("🚀 SCANSIONA PARTITE"):
            if not api_key: st.warning("Inserisci la Chiave API nella barra laterale per procedere.")
            else:
                try:
                    url = f'https://api.the-odds-api.com/v4/sports/{sport[1]}/odds/?apiKey={api_key}&regions=eu'
                    data = requests.get(url).json()
                    
                    if not data:
                        st.info("Nessuna partita disponibile al momento.")
                    
                    for match in data:
                        h, a = match['home_team'], match['away_team']
                        outcomes = match['bookmakers'][0]['markets'][0]['outcomes']
                        o1 = next(x['price'] for x in outcomes if x['name'] == h)
                        ox = next(x['price'] for x in outcomes if x['name'] == 'Draw')
                        o2 = next(x['price'] for x in outcomes if x['name'] == a)

                        res = NeuralEngine.analyze_market(o1, ox, o2)
                        verdetto, v_color = NeuralEngine.get_verdict(res['p1'], o1)

                        with st.container():
                            st.markdown(f'<div class="main-card"><h3>{h} vs {a}</h3><b style="color:{v_color}">{verdetto}</b></div>', unsafe_allow_html=True)
                            c1, c2 = st.columns([2, 1])
                            with c1:
                                fig = go.Figure(data=[go.Pie(labels=[h,'Pareggio',a], values=[res['p1'],res['px'],res['p2']], hole=.4, marker_colors=['#00ff00','#333','#ff4b4b'])])
                                fig.update_layout(height=220, margin=dict(t=0,b=0,l=0,r=0), showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
                                st.plotly_chart(fig, use_container_width=True)
                            with c2:
                                st.write(f"Quota Attuale: **{o1}**")
                                st.write(f"Quota Equa: **{res['fair_1']:.2f}**")
                                if st.button(f"⭐ Salva Pronostico {h}", key=f"btn_{h}"):
                                    conn = sqlite3.connect('neural_bet_pro.db')
                                    conn.execute('INSERT INTO favorites VALUES (?,?,?,?,?)', (st.session_state.user, f"{h} vs {a}", verdetto, str(o1), datetime.now().strftime("%d/%m %H:%M")))
                                    conn.commit()
                                    conn.close()
                                    st.toast("Salvato con successo!")
                except Exception as e: st.error("Errore durante il recupero dei dati.")

    with tab_favs:
        st.subheader("I tuoi salvataggi")
        conn = sqlite3.connect('neural_bet_pro.db')
        favs = pd.read_sql_query('SELECT * FROM favorites WHERE user=?', conn, params=(st.session_state.user,))
        conn.close()
        
        if favs.empty: st.write("Non hai ancora salvato alcun pronostico.")
        else:
            for i, row in favs.iterrows():
                st.markdown(f'<div class="fav-card"><b>{row["match_name"]}</b><br>Esito: {row["prediction"]} | Quota: {row["odds"]} <br><small>Analisi del {row["timestamp"]}</small></div>', unsafe_allow_html=True)
            if st.button("Elimina Tutti i Preferiti"):
                conn = sqlite3.connect('neural_bet_pro.db')
                conn.execute('DELETE FROM favorites WHERE user=?', (st.session_state.user,))
                conn.commit()
                conn.close()
                st.rerun()
