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
    if st.session_state.get('logged_in'):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        bet_json = json.dumps(st.session_state.schedina)
        c.execute("UPDATE users SET current_bet = ? WHERE username = ?", (bet_json, st.session_state.user))
        conn.commit()
        conn.close()

# --- 3. UI & CSS ---
st.set_page_config(page_title="AI NEURAL COMMANDER v16.5", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden; height: 0px; }
    .stApp { background-color: #030508; color: #e0e0e0; }
    .data-card {
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.5), rgba(30, 41, 59, 0.3));
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 20px; padding: 20px; margin-bottom: 15px;
    }
    .user-badge {
        background: rgba(59, 130, 246, 0.2);
        padding: 10px 20px;
        border-radius: 50px;
        border: 1px solid #3b82f6;
        display: inline-block;
        margin-bottom: 20px;
    }
    .bet-row { background: rgba(16, 185, 129, 0.05); border-radius: 10px; padding: 10px; margin-bottom: 8px; border-left: 4px solid #10b981; }
    </style>
""", unsafe_allow_html=True)

# --- 4. INIZIALIZZAZIONE ---
init_db()
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = ""
if 'schedina' not in st.session_state: st.session_state.schedina = []
if 'matches' not in st.session_state: st.session_state.matches = []

# --- 5. SCHERMATA DI ACCESSO ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #3b82f6; margin-top:50px;'>🛡️ NEURAL ACCESS</h1>", unsafe_allow_html=True)
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        mode = st.tabs(["Accedi", "Crea Account"])
        
        with mode[0]:
            u = st.text_input("Username", key="l_u")
            p = st.text_input("Password", type="password", key="l_p")
            if st.button("LOGIN", use_container_width=True):
                conn = sqlite3.connect('users.db')
                c = conn.cursor()
                c.execute('SELECT password, current_bet FROM users WHERE username = ?', (u,))
                res = c.fetchone()
                conn.close()
                if res and check_hashes(p, res[0]):
                    st.session_state.logged_in = True
                    st.session_state.user = u
                    if res[1]: st.session_state.schedina = json.loads(res[1])
                    st.rerun()
                else: st.error("Credenziali non valide")
        
        with mode[1]:
            nu = st.text_input("Nuovo Username", key="r_u")
            npw = st.text_input("Nuova Password", type="password", key="r_p")
            if st.button("REGISTRATI", use_container_width=True):
                if nu and npw:
                    conn = sqlite3.connect('users.db')
                    c = conn.cursor()
                    try:
                        c.execute('INSERT INTO users(username, password, current_bet) VALUES (?,?,?)', (nu, make_hashes(npw), "[]"))
                        conn.commit()
                        st.success("Registrato! Fai il login.")
                    except: st.error("Username occupato")
                    conn.close()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 6. AREA RISERVATA (DOPO LOGIN) ---
else:
    # Sidebar con pulsante Logout
    with st.sidebar:
        st.markdown(f"<div class='user-badge'>👤 {st.session_state.user}</div>", unsafe_allow_html=True)
        st.divider()
        if st.button("🚪 LOGOUT", use_container_width=True):
            save_bet_to_db() # Salva prima di uscire
            st.session_state.logged_in = False
            st.session_state.user = ""
            st.session_state.schedina = []
            st.rerun()
        st.info("Tutte le tue selezioni vengono salvate automaticamente nel database neurale.")

    # Main App Tabs
    t1, t2 = st.tabs(["🚀 ANALISI EVENTI", "📝 LA MIA SCHEDINA"])

    with t1:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            league = st.selectbox("Lega", ["Serie A (SA)", "Premier League (PL)", "La Liga (PD)"])
            l_code = league.split("(")[1].replace(")", "")
        with c2:
            if st.button("🔄 SINCRONIZZA FEED", use_container_width=True):
                headers = {'X-Auth-Token': API_KEY}
                res = requests.get(f"{BASE_URL}competitions/{l_code}/matches?status=SCHEDULED", headers=headers)
                if res.status_code == 200: st.session_state.matches = res.json().get('matches', [])

        matches = st.session_state.get('matches', [])
        if matches:
            labels = [f"{datetime.fromisoformat(m['utcDate'].replace('Z', '+00:00')).strftime('%d/%m - %H:%M')} | {m['homeTeam']['name']} vs {m['awayTeam']['name']}" for m in matches]
            selected = st.selectbox("Seleziona Match", ["---"] + labels)
            
            if selected != "---":
                m_data = matches[labels.index(selected)]
                h_n, a_n = m_data['homeTeam']['name'], m_data['awayTeam']['name']
                p = np.random.dirichlet(np.array([12, 6, 7]), size=1)[0]
                
                st.markdown(f"<h2 style='text-align:center;'>{h_n} vs {a_n}</h2>", unsafe_allow_html=True)
                
                # Selezione rapida quota
                st.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                rl = ['1', 'X', '2']
                for i, col in enumerate([c1, c2, c3]):
                    q = 1/p[i]
                    if col.button(f"{rl[i]} @ {q:.2f}", key=f"b_{i}", use_container_width=True):
                        st.session_state.schedina.append({"m": f"{h_n}-{a_n}", "s": rl[i], "q": q})
                        save_bet_to_db()
                        st.toast(f"Aggiunto {rl[i]}!")
                st.markdown("</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with t2:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.subheader("📋 Schedina Salvata")
        if not st.session_state.schedina:
            st.info("Nessuna giocata presente.")
        else:
            tot = 1.0
            for i, bet in enumerate(st.session_state.schedina):
                col_a, col_b = st.columns([5, 1])
                col_a.markdown(f"<div class='bet-row'>{bet['m']} -> <b>{bet['s']}</b> @ {bet['q']:.2f}</div>", unsafe_allow_html=True)
                if col_b.button("🗑️", key=f"d_{i}"):
                    st.session_state.schedina.pop(i)
                    save_bet_to_db()
                    st.rerun()
                tot *= bet['q']
            st.divider()
            st.metric("QUOTA TOTALE", f"x {tot:.2f}")
            if st.button("SVUOTA SCHEDINA"):
                st.session_state.schedina = []
                save_bet_to_db()
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
