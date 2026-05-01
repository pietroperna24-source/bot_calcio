import streamlit as st
import time
import requests
import random
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sqlite3
import hashlib
import json
from datetime import datetime, timedelta

# --- 1. CONFIGURAZIONE API ---
API_KEY = "ea1f03fb102749fa9140e20b184f2996" 
BASE_URL = "https://api.football-data.org/v4/"

# --- 2. DATABASE E SICUREZZA ---
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, current_bet TEXT)''')
    conn.commit()
    conn.close()

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

def save_bet_to_db():
    if st.session_state.logged_in:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        bet_json = json.dumps(st.session_state.schedina)
        c.execute("UPDATE users SET current_bet = ? WHERE username = ?", (bet_json, st.session_state.user))
        conn.commit()
        conn.close()

# --- 3. UI & CSS ---
st.set_page_config(page_title="AI NEURAL COMMANDER v17.5", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden; height: 0px; }
    .stApp { background-color: #030508; color: #e0e0e0; }
    .data-card {
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.5), rgba(30, 41, 59, 0.3));
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 20px; padding: 20px; margin-bottom: 15px; backdrop-filter: blur(10px);
    }
    .terminal-text { font-family: 'Courier New', monospace; color: #10b981; font-size: 0.85rem; margin: 0; }
    .absent-card { background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2); padding: 8px; border-radius: 10px; margin-top: 5px; font-size: 0.8rem; }
    .bet-row { background: rgba(16, 185, 129, 0.05); border-radius: 10px; padding: 10px; margin-bottom: 8px; border-left: 4px solid #10b981; }
    
    /* Stile specifico per il box utente in sidebar */
    .sidebar-user-box {
        background: rgba(59, 130, 246, 0.1);
        padding: 15px;
        border-radius: 15px;
        border: 1px solid #3b82f6;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. INIZIALIZZAZIONE ---
init_db()
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = ""
if 'schedina' not in st.session_state: st.session_state.schedina = []
if 'matches' not in st.session_state: st.session_state.matches = []
if 'last_selected' not in st.session_state: st.session_state.last_selected = None

# --- 5. SCHERMATA DI ACCESSO (GATEKEEPER) ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color: #3b82f6;'>🛡️ AI NEURAL COMMANDER ACCESS</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        choice = st.radio("Scegli Azione", ["Login", "Registrazione"], horizontal=True)
        
        if choice == "Login":
            user = st.text_input("Username")
            pw = st.text_input("Password", type="password")
            if st.button("ENTRA NEL SISTEMA", use_container_width=True):
                conn = sqlite3.connect('users.db')
                c = conn.cursor()
                c.execute('SELECT password, current_bet FROM users WHERE username = ?', (user,))
                data = c.fetchone()
                conn.close()
                if data and check_hashes(pw, data[0]):
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    if data[1]: st.session_state.schedina = json.loads(data[1])
                    st.rerun()
                else: st.error("Accesso negato: credenziali non valide.")
        
        else:
            new_user = st.text_input("Crea Username")
            new_pw = st.text_input("Crea Password", type="password")
            if st.button("REGISTRA ACCOUNT", use_container_width=True):
                if new_user and new_pw:
                    conn = sqlite3.connect('users.db')
                    c = conn.cursor()
                    try:
                        c.execute('INSERT INTO users(username, password, current_bet) VALUES (?,?,?)', (new_user, make_hashes(new_pw), "[]"))
                        conn.commit()
                        st.success("Account creato! Fai il login per entrare.")
                    except: st.error("Errore: username già esistente.")
                    conn.close()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 6. INTERFACCIA INTERNA (DOPO LOGIN) ---
else:
    # --- SIDEBAR CON PULSANTE LOGOUT BEN VISIBILE ---
    with st.sidebar:
        st.markdown(f"""
            <div class="sidebar-user-box">
                <small style="color: #94a3b8;">SESSIONE ATTIVA</small><br>
                <b style="font-size: 1.2rem; color: #fff;">{st.session_state.user}</b>
            </div>
        """, unsafe_allow_html=True)
        
        # IL PULSANTE DI LOGOUT
        if st.button("🚪 ESCI (LOGOUT)", use_container_width=True, type="primary"):
            st.session_state.logged_in = False
            st.session_state.user = ""
            st.session_state.schedina = []
            st.session_state.last_selected = None
            st.rerun()
            
        st.divider()
        st.write("⚙️ Impostazioni Profilo")
        st.caption("AI Neural Commander v17.5 Gold")

    # --- TAB CONTENUTI ---
    tab_analisi, tab_schedina = st.tabs(["🚀 ANALISI LIVE", "📝 LA MIA SCHEDINA"])

    with tab_analisi:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1])
        with c1:
            league = st.selectbox("🏆 Seleziona Lega", ["Serie A (SA)", "Premier League (PL)", "La Liga (PD)"])
            l_code = league.split("(")[1].replace(")", "")
        with c2:
            if st.button("🔄 AGGIORNA FEED API", use_container_width=True):
                headers = {'X-Auth-Token': API_KEY}
                res = requests.get(f"{BASE_URL}competitions/{l_code}/matches?status=SCHEDULED", headers=headers)
                if res.status_code == 200: st.session_state.matches = res.json().get('matches', [])

        matches = st.session_state.get('matches', [])
        if matches:
            labels = [f"{datetime.fromisoformat(m['utcDate'].replace('Z', '+00:00')).strftime('%H:%M')} | {m['homeTeam']['name']} vs {m['awayTeam']['name']}" for m in matches]
            selected = st.selectbox("🎯 Seleziona Evento", ["---"] + labels)
            
            if selected != "---":
                # Animazione Hacker
                if st.session_state.last_selected != selected:
                    placeholder = st.empty()
                    with placeholder.container():
                        st.markdown('<div class="data-card">', unsafe_allow_html=True)
                        st.markdown("<p class='terminal-text'>[SISTEMA]: Inizializzazione Deep Scan...</p>", unsafe_allow_html=True)
                        pb = st.progress(0)
                        for i, s in enumerate(["📡 Link API...", "🧬 Scan Power Index...", "🚑 Verifica Infermeria...", "✅ Completato."]):
                            time.sleep(0.4)
                            st.markdown(f"<p class='terminal-text' style='opacity:0.7;'>{s}</p>", unsafe_allow_html=True)
                            pb.progress((i+1)*25)
                        st.markdown('</div>', unsafe_allow_html=True)
                    placeholder.empty()
                    st.session_state.last_selected = selected

                m_data = matches[labels.index(selected)]
                h_n, a_n = m_data['homeTeam']['name'], m_data['awayTeam']['name']
                
                # Simulazione Dati Deep
                p = np.random.dirichlet(np.array([12, 6, 7]), size=1)[0]
                radar_val = [random.randint(65, 98) for _ in range(5)]
                
                st.markdown(f"<h2 style='text-align:center;'>{h_n.upper()} vs {a_n.upper()}</h2>", unsafe_allow_html=True)
                
                col_l, col_m, col_r = st.columns([1, 1.5, 1])
                with col_l:
                    st.markdown('<div class="data-card">', unsafe_allow_html=True)
                    st.write("🚑 **Assenti Home**")
                    st.markdown("<div class='absent-card'><b>L. Martinez</b><br>Infortunio Muscolare</div>", unsafe_allow_html=True)
                    st.divider()
                    st.write(f"⚖️ Arbitro: {random.choice(['D. Orsato', 'M. Oliver'])}")
                    st.markdown('</div>', unsafe_allow_html=True)

                with col_m:
                    st.markdown('<div class="data-card" style="text-align:center;">', unsafe_allow_html=True)
                    st.subheader("🎯 Neural Probabilities")
                    c1, c2, c3 = st.columns(3)
                    res_l = ['1', 'X', '2']
                    for i, col in enumerate([c1, c2, c3]):
                        q = 1/p[i]
                        if col.button(f"{res_l[i]} @ {q:.2f}", key=f"btn_{i}", use_container_width=True):
                            st.session_state.schedina.append({"m": f"{h_n}-{a_n}", "s": res_l[i], "q": q})
                            save_bet_to_db()
                            st.toast(f"✅ {res_l[i]} aggiunto!")
                    
                    fig = go.Figure(data=go.Scatterpolar(r=radar_val, theta=['Att','Dif','For','Fis','Tat'], fill='toself', line_color='#10b981'))
                    fig.update_layout(polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(visible=False, range=[0, 100])), showlegend=False, height=200, margin=dict(t=20,b=20,l=35,r=35), paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                with col_r:
                    st.markdown('<div class="data-card">', unsafe_allow_html=True)
                    st.write("🚑 **Assenti Away**")
                    st.markdown("<div class='absent-card'><b>J. Grealish</b><br>Squalifica</div>", unsafe_allow_html=True)
                    st.divider()
                    st.write("⚽ Extra Markets")
                    if st.button("Over 2.5", use_container_width=True):
                        st.session_state.schedina.append({"m": f"{h_n}-{a_n}", "s": "Over 2.5", "q": 1.85})
                        save_bet_to_db()
                    st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_schedina:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.subheader("📋 Schedina Salvata nel Profilo")
        if not st.session_state.schedina: st.info("La tua schedina è vuota.")
        else:
            total_odd = 1.0
            for i, bet in enumerate(st.session_state.schedina):
                col_i, col_d = st.columns([4, 1])
                col_i.markdown(f"<div class='bet-row'>{bet['m']} - <b>{bet['s']}</b> @ {bet['q']:.2f}</div>", unsafe_allow_html=True)
                if col_d.button("🗑️", key=f"del_{i}"):
                    st.session_state.schedina.pop(i)
                    save_bet_to_db()
                    st.rerun()
                total_odd *= bet['q']
            st.divider()
            st.metric("QUOTA TOTALE", f"x {total_odd:.2f}")
            if st.button("SVUOTA TUTTO", use_container_width=True):
                st.session_state.schedina = []
                save_bet_to_db()
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
