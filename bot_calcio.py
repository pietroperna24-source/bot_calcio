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
                 (username TEXT PRIMARY KEY, password TEXT, current_bet TEXT, theme TEXT)''')
    conn.commit()
    conn.close()

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def save_bet_to_db():
    if st.session_state.logged_in:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        bet_json = json.dumps(st.session_state.schedina)
        c.execute("UPDATE users SET current_bet = ? WHERE username = ?", (bet_json, st.session_state.user))
        conn.commit()
        conn.close()

# --- 3. UI & TEMI ---
st.set_page_config(page_title="AI NEURAL COMMANDER v18", layout="wide")

# Gestione Temi Dinamici
theme_color = st.session_state.get('theme_color', '#3b82f6') # Default Blu

st.markdown(f"""
    <style>
    header[data-testid="stHeader"] {{ visibility: hidden; height: 0px; }}
    .stApp {{ background-color: #030508; color: #e0e0e0; }}
    .data-card {{
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.5), rgba(30, 41, 59, 0.3));
        border: 1px solid {theme_color}44;
        border-radius: 20px; padding: 20px; margin-bottom: 15px; backdrop-filter: blur(10px);
    }}
    .terminal-text {{ font-family: 'Courier New', monospace; color: #10b981; font-size: 0.85rem; }}
    .bet-row {{ background: rgba(16, 185, 129, 0.05); border-radius: 10px; padding: 10px; margin-bottom: 8px; border-left: 4px solid #10b981; }}
    </style>
""", unsafe_allow_html=True)

# --- 4. INIZIALIZZAZIONE ---
init_db()
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = ""
if 'schedina' not in st.session_state: st.session_state.schedina = []
if 'matches' not in st.session_state: st.session_state.matches = []
if 'last_selected' not in st.session_state: st.session_state.last_selected = None

# --- 5. LOGICA ACCESSO ---
if not st.session_state.logged_in:
    st.markdown(f"<h1 style='text-align: center; color: {theme_color};'>🛡️ NEURAL COMMANDER ACCESS</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        mode = st.radio("Scegli", ["Login", "Registrazione"], horizontal=True)
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        
        if mode == "Login":
            if st.button("ACCEDI AL SISTEMA", use_container_width=True):
                conn = sqlite3.connect('users.db')
                c = conn.cursor()
                c.execute('SELECT password, current_bet, theme FROM users WHERE username = ?', (u,))
                data = c.fetchone()
                conn.close()
                if data and data[0] == make_hashes(p):
                    st.session_state.logged_in = True
                    st.session_state.user = u
                    st.session_state.schedina = json.loads(data[1]) if data[1] else []
                    if data[2]: st.session_state.theme_color = data[2]
                    st.rerun()
                else: st.error("Errore credenziali.")
        else:
            if st.button("CREA ACCOUNT", use_container_width=True):
                conn = sqlite3.connect('users.db')
                c = conn.cursor()
                try:
                    c.execute('INSERT INTO users(username, password, current_bet, theme) VALUES (?,?,?,?)', 
                              (u, make_hashes(p), "[]", "#3b82f6"))
                    conn.commit()
                    st.success("Account creato!")
                except: st.error("Username occupato.")
                conn.close()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 6. INTERFACCIA DOPO LOGIN ---
else:
    # SISTEMA A 3 TAB (TUTTO VISIBILE SENZA SIDEBAR)
    tab_analisi, tab_schedina, tab_settings = st.tabs(["🚀 ANALISI LIVE", "📝 LA MIA SCHEDINA", "⚙️ IMPOSTAZIONI & LOGOUT"])

    # --- TAB ANALISI ---
    with tab_analisi:
        st.markdown(f"<p style='color:{theme_color}'>Benvenuto Operatore: <b>{st.session_state.user}</b></p>", unsafe_allow_html=True)
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            league = st.selectbox("🏆 Lega", ["Serie A (SA)", "Premier League (PL)", "La Liga (PD)"])
            l_code = league.split("(")[1].replace(")", "")
        with c2:
            if st.button("🔄 SINCRONIZZA API", use_container_width=True):
                res = requests.get(f"{BASE_URL}competitions/{l_code}/matches?status=SCHEDULED", headers={'X-Auth-Token': API_KEY})
                if res.status_code == 200: st.session_state.matches = res.json().get('matches', [])
        
        matches = st.session_state.get('matches', [])
        if matches:
            labels = [f"{datetime.fromisoformat(m['utcDate'].replace('Z', '+00:00')).strftime('%H:%M')} | {m['homeTeam']['name']} vs {m['awayTeam']['name']}" for m in matches]
            selected = st.selectbox("🎯 Target", ["---"] + labels)
            
            if selected != "---":
                if st.session_state.last_selected != selected:
                    with st.status("🧬 Deep Scan In Corso...", expanded=True):
                        time.sleep(0.8)
                    st.session_state.last_selected = selected

                m_data = matches[labels.index(selected)]
                h_n, a_n = m_data['homeTeam']['name'], m_data['awayTeam']['name']
                p = np.random.dirichlet(np.array([12, 6, 7]), size=1)[0]
                
                st.markdown(f"<h2 style='text-align:center;'>{h_n.upper()} vs {a_n.upper()}</h2>", unsafe_allow_html=True)
                
                col_l, col_m, col_r = st.columns([1, 1.5, 1])
                with col_l:
                    st.markdown('<div class="data-card">', unsafe_allow_html=True)
                    st.write("🚑 **Assenti Home**")
                    st.caption("• L. Martinez (Muscolare)")
                    st.caption("• N. Barella (Squalifica)")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col_m:
                    st.markdown('<div class="data-card" style="text-align:center;">', unsafe_allow_html=True)
                    st.subheader("🎯 Neural Betting")
                    c1, c2, c3 = st.columns(3)
                    res_l = ['1', 'X', '2']
                    for i, col in enumerate([c1, c2, c3]):
                        q = 1/p[i]
                        if col.button(f"{res_l[i]} @ {q:.2f}", key=f"b_{i}", use_container_width=True):
                            st.session_state.schedina.append({"m": f"{h_n}-{a_n}", "s": res_l[i], "q": q})
                            save_bet_to_db()
                            st.toast("Salvato!")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col_r:
                    st.markdown('<div class="data-card">', unsafe_allow_html=True)
                    st.write("🚑 **Assenti Away**")
                    st.caption("• K. Walker (Dubbio)")
                    st.caption("• Rodri (Crociato)")
                    st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB SCHEDINA ---
    with tab_schedina:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.subheader("📋 Il Tuo Archivio")
        if not st.session_state.schedina: st.write("Sposta le analisi qui cliccando sulle quote.")
        else:
            total = 1.0
            for i, bet in enumerate(st.session_state.schedina):
                col_i, col_d = st.columns([5, 1])
                col_i.markdown(f"<div class='bet-row'>{bet['m']} - <b>{bet['s']}</b> @ {bet['q']:.2f}</div>", unsafe_allow_html=True)
                if col_d.button("🗑️", key=f"del_{i}"):
                    st.session_state.schedina.pop(i); save_bet_to_db(); st.rerun()
                total *= bet['q']
            st.divider()
            st.metric("QUOTA TOTALE", f"x {total:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB IMPOSTAZIONI & LOGOUT (NOVITÀ) ---
    with tab_settings:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.subheader("⚙️ Gestione Account")
        
        # Cambio Username
        new_u = st.text_input("Cambia Username", value=st.session_state.user)
        if st.button("Aggiorna Nome Utente"):
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            try:
                c.execute("UPDATE users SET username = ? WHERE username = ?", (new_u, st.session_state.user))
                conn.commit()
                st.session_state.user = new_u
                st.success("Username aggiornato!")
            except: st.error("Errore: username già preso.")
            conn.close()

        st.divider()
        
        # Cambio Password
        new_p = st.text_input("Nuova Password", type="password")
        if st.button("Aggiorna Password"):
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            c.execute("UPDATE users SET password = ? WHERE username = ?", (make_hashes(new_p), st.session_state.user))
            conn.commit()
            conn.close()
            st.success("Password modificata correttamente!")

        st.divider()

        # Cambio Tema
        st.subheader("🎨 Personalizzazione")
        color = st.color_picker("Scegli il colore dell'interfaccia", theme_color)
        if st.button("Salva Tema"):
            st.session_state.theme_color = color
            conn = sqlite3.connect('users.db')
            c = conn.cursor()
            c.execute("UPDATE users SET theme = ? WHERE username = ?", (color, st.session_state.user))
            conn.commit()
            conn.close()
            st.rerun()

        st.divider()
        
        # IL PULSANTE DI LOGOUT (GIGANTE E ROSSO)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 ESCI DAL SISTEMA (LOGOUT)", use_container_width=True, type="primary"):
            st.session_state.logged_in = False
            st.session_state.user = ""
            st.session_state.schedina = []
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
