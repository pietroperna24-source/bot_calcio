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

# --- 2. DATABASE ---
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, current_bet TEXT, theme TEXT)''')
    try:
        c.execute("ALTER TABLE users ADD COLUMN theme TEXT DEFAULT '#3b82f6'")
    except sqlite3.OperationalError:
        pass 
    conn.commit()
    conn.close()

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def save_bet_to_db():
    if st.session_state.get('logged_in'):
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        bet_json = json.dumps(st.session_state.schedina)
        c.execute("UPDATE users SET current_bet = ? WHERE username = ?", (bet_json, st.session_state.user))
        conn.commit()
        conn.close()

# --- 3. INIZIALIZZAZIONE ---
init_db()
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = ""
if 'schedina' not in st.session_state: st.session_state.schedina = []
if 'matches' not in st.session_state: st.session_state.matches = []
if 'theme_color' not in st.session_state: st.session_state.theme_color = "#3b82f6"
if 'last_selected' not in st.session_state: st.session_state.last_selected = None

# --- 4. UI & STILE ---
st.set_page_config(page_title="AI NEURAL COMMANDER v20.1", layout="wide")
t_color = st.session_state.theme_color

st.markdown(f"""
    <style>
    header[data-testid="stHeader"] {{ visibility: hidden; }}
    .stApp {{ background-color: #030508; color: #e0e0e0; }}
    .data-card {{
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.5), rgba(30, 41, 59, 0.3));
        border: 1px solid {t_color}66;
        border-radius: 20px; padding: 20px; margin-bottom: 15px; backdrop-filter: blur(10px);
    }}
    .bet-row {{ background: rgba(16, 185, 129, 0.1); border-radius: 10px; padding: 10px; margin-bottom: 8px; border-left: 4px solid #10b981; }}
    .terminal-text {{ font-family: 'Courier New', monospace; color: #10b981; font-size: 0.85rem; }}
    </style>
""", unsafe_allow_html=True)

# --- 5. SCHERMATA LOGIN ---
if not st.session_state.logged_in:
    st.markdown(f"<h1 style='text-align:center; color:{t_color};'>🛡️ NEURAL ACCESS</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        mode = st.radio("Azione", ["Entra", "Registrati"], horizontal=True)
        u_in = st.text_input("Username")
        p_in = st.text_input("Password", type="password")
        
        if mode == "Entra":
            if st.button("LOG IN", use_container_width=True):
                conn = sqlite3.connect('users.db'); c = conn.cursor()
                c.execute('SELECT password, current_bet, theme FROM users WHERE username = ?', (u_in,))
                data = c.fetchone(); conn.close()
                if data and data[0] == make_hashes(p_in):
                    st.session_state.logged_in = True
                    st.session_state.user = u_in
                    st.session_state.schedina = json.loads(data[1]) if data[1] else []
                    st.session_state.theme_color = data[2] if data[2] else "#3b82f6"
                    st.rerun()
                else: st.error("Dati errati.")
        else:
            if st.button("CREA ACCOUNT", use_container_width=True):
                if u_in and p_in:
                    conn = sqlite3.connect('users.db'); c = conn.cursor()
                    try:
                        c.execute('INSERT INTO users(username, password, current_bet, theme) VALUES (?,?,?,?)', 
                                  (u_in, make_hashes(p_in), "[]", "#3b82f6"))
                        conn.commit(); st.success("Creato! Accedi ora.")
                    except: st.error("Username occupato.")
                    conn.close()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 6. AREA PRIVATA ---
else:
    t1, t2, t3 = st.tabs(["🚀 ANALISI LIVE", "📝 SCHEDINA", "⚙️ IMPOSTAZIONI ACCOUNT"])

    with t1:
        st.markdown(f"<p style='color:{t_color}'>Operatore: <b>{st.session_state.user}</b></p>", unsafe_allow_html=True)
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            league = st.selectbox("Lega", ["Serie A (SA)", "Premier League (PL)", "La Liga (PD)"])
            l_code = league.split("(")[1].replace(")", "")
        with c2:
            if st.button("🔄 SINCRONIZZA", use_container_width=True):
                res = requests.get(f"{BASE_URL}competitions/{l_code}/matches?status=SCHEDULED", headers={'X-Auth-Token': API_KEY})
                if res.status_code == 200: st.session_state.matches = res.json().get('matches', [])
        
        matches = st.session_state.get('matches', [])
        if matches:
            labels = [f"{datetime.fromisoformat(m['utcDate'].replace('Z', '+00:00')).strftime('%H:%M')} | {m['homeTeam']['name']} vs {m['awayTeam']['name']}" for m in matches]
            selected = st.selectbox("Seleziona Match", ["---"] + labels)
            if selected != "---":
                m_data = matches[labels.index(selected)]
                h_n, a_n = m_data['homeTeam']['name'], m_data['awayTeam']['name']
                st.markdown(f"<h3 style='text-align:center;'>{h_n} vs {a_n}</h3>", unsafe_allow_html=True)
                p = np.random.dirichlet(np.array([12, 6, 7]), size=1)[0]
                cols = st.columns(3)
                for i, lab in enumerate(['1', 'X', '2']):
                    q = 1/p[i]
                    if cols[i].button(f"{lab} @ {q:.2f}", use_container_width=True, key=f"b_{i}"):
                        st.session_state.schedina.append({"m": f"{h_n}-{a_n}", "s": lab, "q": q})
                        save_bet_to_db(); st.toast("Aggiunto!")
        st.markdown('</div>', unsafe_allow_html=True)

    with t2:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.subheader("📋 Schedina")
        if not st.session_state.schedina: st.write("Vuota.")
        else:
            total = 1.0
            for i, bet in enumerate(st.session_state.schedina):
                ci, cd = st.columns([5, 1])
                ci.markdown(f"<div class='bet-row'>{bet['m']} - <b>{bet['s']}</b> @ {bet['q']:.2f}</div>", unsafe_allow_html=True)
                if cd.button("🗑️", key=f"del_{i}"):
                    st.session_state.schedina.pop(i); save_bet_to_db(); st.rerun()
                total *= bet['q']
            st.metric("TOTALE", f"x {total:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)

    with t3:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.subheader("👤 Gestione Profilo")
        
        # MODIFICA USERNAME
        new_username = st.text_input("Nuovo Username", value=st.session_state.user)
        if st.button("Aggiorna Username"):
            conn = sqlite3.connect('users.db'); c = conn.cursor()
            try:
                c.execute("UPDATE users SET username = ? WHERE username = ?", (new_username, st.session_state.user))
                conn.commit(); st.session_state.user = new_username; st.success("Username aggiornato!")
            except: st.error("Errore: username occupato.")
            conn.close()

        st.divider()

        # MODIFICA PASSWORD
        new_pass = st.text_input("Nuova Password", type="password")
        if st.button("Cambia Password"):
            if new_pass:
                conn = sqlite3.connect('users.db'); c = conn.cursor()
                c.execute("UPDATE users SET password = ? WHERE username = ?", (make_hashes(new_pass), st.session_state.user))
                conn.commit(); conn.close(); st.success("Password cambiata!")
            else: st.warning("Inserisci una password valida.")

        st.divider()

        # TEMA E LOGOUT
        st.subheader("🎨 Personalizzazione")
        new_color = st.color_picker("Colore Tema", t_color)
        if st.button("Salva Tema"):
            st.session_state.theme_color = new_color
            conn = sqlite3.connect('users.db'); c = conn.cursor()
            c.execute("UPDATE users SET theme = ? WHERE username = ?", (new_color, st.session_state.user))
            conn.commit(); conn.close(); st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 LOGOUT", use_container_width=True, type="primary"):
            st.session_state.logged_in = False; st.session_state.user = ""; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
