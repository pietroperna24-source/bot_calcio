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
st.set_page_config(page_title="AI NEURAL COMMANDER v16", layout="wide")

st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden; height: 0px; }
    .stApp { background-color: #030508; color: #e0e0e0; }
    .data-card {
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.5), rgba(30, 41, 59, 0.3));
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 20px; padding: 20px; margin-bottom: 15px;
    }
    .terminal-text { font-family: 'Courier New', monospace; color: #10b981; font-size: 0.85rem; }
    .quota-box { background: rgba(255, 255, 255, 0.03); border-radius: 12px; padding: 10px; text-align: center; border: 1px solid rgba(255, 255, 255, 0.05); }
    .bet-row { background: rgba(16, 185, 129, 0.05); border-radius: 10px; padding: 10px; margin-bottom: 8px; border-left: 4px solid #10b981; }
    </style>
""", unsafe_allow_html=True)

# --- 4. INIZIALIZZAZIONE ---
init_db()
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = ""
if 'schedina' not in st.session_state: st.session_state.schedina = []
if 'matches' not in st.session_state: st.session_state.matches = []
if 'last_selected' not in st.session_state: st.session_state.last_selected = None

# --- 5. LOGICA DI ACCESSO (SCHERMATA PRINCIPALE) ---
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
                else:
                    st.error("Accesso negato: credenziali errate.")
        
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
                        st.success("Account creato con successo! Ora effettua il login.")
                    except:
                        st.error("Errore: lo username potrebbe essere già occupato.")
                    conn.close()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 6. INTERFACCIA SITO (DENTRO DOPO LOGIN) ---
else:
    # Barra superiore di stato
    st.markdown(f"""
        <div style='display: flex; justify-content: space-between; align-items: center; padding: 10px; background: rgba(59, 130, 246, 0.1); border-radius: 10px; margin-bottom: 20px;'>
            <span>Benvenuto, <b>{st.session_state.user}</b></span>
            <button onclick="window.location.reload()">Aggiorna</button>
        </div>
    """, unsafe_allow_html=True)
    if st.sidebar.button("LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()

    tab_analisi, tab_schedina = st.tabs(["🚀 ANALISI LIVE", "📝 SCHEDINA SALVATA"])

    with tab_analisi:
        # Codice Analisi (Versione v14-v15)
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1])
        with c1:
            league = st.selectbox("🏆 Campionato", ["Serie A (SA)", "Premier League (PL)", "La Liga (PD)"])
            l_code = league.split("(")[1].replace(")", "")
        with c2:
            if st.button("🔄 AGGIORNA FEED API", use_container_width=True):
                headers = {'X-Auth-Token': API_KEY}
                res = requests.get(f"{BASE_URL}competitions/{l_code}/matches?status=SCHEDULED", headers=headers)
                if res.status_code == 200: st.session_state.matches = res.json().get('matches', [])

        matches = st.session_state.get('matches', [])
        if matches:
            labels = [f"{datetime.fromisoformat(m['utcDate'].replace('Z', '+00:00')).strftime('%d/%m - %H:%M')} | {m['homeTeam']['name']} vs {m['awayTeam']['name']}" for m in matches]
            selected = st.selectbox("🎯 Seleziona Evento", ["---"] + labels)
            
            if selected != "---":
                # Animazione Caricamento
                if st.session_state.last_selected != selected:
                    with st.status("🧬 Deep Scan...", expanded=True):
                        time.sleep(1.0)
                    st.session_state.last_selected = selected

                m_data = matches[labels.index(selected)]
                h_n, a_n = m_data['homeTeam']['name'], m_data['awayTeam']['name']
                
                # Simulazione Dati
                p = np.random.dirichlet(np.array([12, 6, 7]), size=1)[0]
                
                st.markdown(f"<h2 style='text-align:center;'>{h_n.upper()} vs {a_n.upper()}</h2>", unsafe_allow_html=True)
                
                col_l, col_m, col_r = st.columns([1, 1.5, 1])
                with col_m:
                    st.markdown('<div class="data-card" style="text-align:center;">', unsafe_allow_html=True)
                    st.subheader("🎯 Quote & Probabilità")
                    c1, c2, c3 = st.columns(3)
                    res_l = ['1', 'X', '2']
                    for i, col in enumerate([c1, c2, c3]):
                        q = 1/p[i]
                        if col.button(f"{res_l[i]} @ {q:.2f}", use_container_width=True):
                            st.session_state.schedina.append({"m": f"{h_n}-{a_n}", "s": res_l[i], "q": q})
                            save_bet_to_db()
                            st.toast("Salvato!")
                    st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_schedina:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.subheader("📋 Riepilogo Permanente")
        if not st.session_state.schedina:
            st.write("Nessun evento salvato nel database.")
        else:
            total_odd = 1.0
            for i, bet in enumerate(st.session_state.schedina):
                col_inf, col_rem = st.columns([4, 1])
                col_inf.markdown(f"<div class='bet-row'>{bet['m']} - <b>{bet['s']}</b> @ {bet['q']:.2f}</div>", unsafe_allow_html=True)
                if col_rem.button("🗑️", key=f"del_{i}"):
                    st.session_state.schedina.pop(i)
                    save_bet_to_db()
                    st.rerun()
                total_odd *= bet['q']
            st.divider()
            st.metric("QUOTA TOTALE", f"x {total_odd:.2f}")
            if st.button("SVUOTA TUTTO"):
                st.session_state.schedina = []
                save_bet_to_db()
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
