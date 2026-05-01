import streamlit as st
import time
import requests
import random
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import sqlite3
import hashlib
from datetime import datetime, timedelta

# --- 1. CONFIGURAZIONE API ---
API_KEY = "ea1f03fb102749fa9140e20b184f2996" 
BASE_URL = "https://api.football-data.org/v4/"

# --- 2. DATABASE SQLITE (Gestione Utenti e Schedine) ---
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # Tabella Utenti
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, current_bet TEXT)''')
    conn.commit()
    conn.close()

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

# --- 3. UI & CSS ---
st.set_page_config(page_title="AI NEURAL COMMANDER v15.0", layout="wide")

st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden; height: 0px; }
    .stApp { background-color: #030508; color: #e0e0e0; }
    .data-card {
        background: linear-gradient(145deg, rgba(15, 23, 42, 0.5), rgba(30, 41, 59, 0.3));
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 20px; padding: 20px; margin-bottom: 15px;
    }
    .bet-row {
        background: rgba(255, 255, 255, 0.03); border-radius: 15px;
        padding: 15px; margin-bottom: 10px; border-left: 5px solid #10b981;
    }
    </style>
""", unsafe_allow_html=True)

# --- 4. LOGICA DI SESSIONE ---
init_db()
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = ""
if 'schedina' not in st.session_state: st.session_state.schedina = []
if 'matches' not in st.session_state: st.session_state.matches = []

# Funzione per salvare la schedina nel DB
def save_bet_to_db():
    if st.session_state.logged_in:
        import json
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        bet_json = json.dumps(st.session_state.schedina)
        c.execute("UPDATE users SET current_bet = ? WHERE username = ?", (bet_json, st.session_state.user))
        conn.commit()
        conn.close()

# --- 5. MAIN APP CON TABS ---
st.markdown("<h1 style='text-align: center; color: #3b82f6;'>🧠 NEURAL COMMANDER PRO</h1>", unsafe_allow_html=True)

tab_login, tab_analisi, tab_schedina = st.tabs(["👤 PROFILO", "🚀 ANALISI LIVE", "📝 LA MIA SCHEDINA"])

# --- TAB LOGIN ---
with tab_login:
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    if not st.session_state.logged_in:
        sub_tab1, sub_tab2 = st.tabs(["Login", "Registrazione"])
        
        with sub_tab1:
            user = st.text_input("Username", key="login_user")
            pw = st.text_input("Password", type="password", key="login_pw")
            if st.button("Accedi"):
                conn = sqlite3.connect('users.db')
                c = conn.cursor()
                c.execute('SELECT password, current_bet FROM users WHERE username = ?', (user,))
                data = c.fetchone()
                conn.close()
                if data and check_hashes(pw, data[0]):
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    # Carica schedina salvata
                    import json
                    if data[1]: st.session_state.schedina = json.loads(data[1])
                    st.success(f"Bentornato {user}!")
                    st.rerun()
                else:
                    st.error("Credenziali errate.")

        with sub_tab2:
            new_user = st.text_input("Scegli Username", key="reg_user")
            new_pw = st.text_input("Scegli Password", type="password", key="reg_pw")
            if st.button("Registrati"):
                conn = sqlite3.connect('users.db')
                c = conn.cursor()
                try:
                    c.execute('INSERT INTO users(username, password) VALUES (?,?)', (new_user, make_hashes(new_pw)))
                    conn.commit()
                    st.success("Account creato! Ora puoi accedere.")
                except:
                    st.error("Username già esistente.")
                conn.close()
    else:
        st.write(f"Connesso come: **{st.session_state.user}**")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user = ""
            st.session_state.schedina = []
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# --- TAB ANALISI (Logica v14 con aggiunta salvataggio DB) ---
with tab_analisi:
    # ... [Inserire qui la logica di selezione match e analisi delle versioni precedenti] ...
    # Quando l'utente aggiunge una scommessa:
    # st.session_state.schedina.append(new_bet)
    # save_bet_to_db() # <--- Chiamata al DB
    st.info("Loggati per salvare permanentemente le tue analisi.")
    
    # Esempio rapido pulsante (riutilizza il tuo codice v14 qui)
    if st.button("Aggiungi Test (Esempio)"):
        st.session_state.schedina.append({"m": "Inter-Milan", "s": "1", "q": 1.85})
        save_bet_to_db()
        st.toast("Salvato nel database!")

# --- TAB SCHEDINA ---
with tab_schedina:
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    if st.session_state.logged_in:
        st.caption(f"💾 Schedina sincronizzata con l'account: {st.session_state.user}")
    
    if not st.session_state.schedina:
        st.write("Schedina vuota.")
    else:
        total = 1.0
        for i, bet in enumerate(st.session_state.schedina):
            st.markdown(f"<div class='bet-row'>{bet['m']} - {bet['s']} @ {bet['q']:.2f}</div>", unsafe_allow_html=True)
            total *= bet['q']
        st.metric("MOLTIPLICATORE", f"x {total:.2f}")
        
        if st.button("Svuota e Sincronizza"):
            st.session_state.schedina = []
            save_bet_to_db()
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
