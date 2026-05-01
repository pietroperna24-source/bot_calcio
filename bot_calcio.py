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
import base64
from io import BytesIO
from PIL import Image
from datetime import datetime

# --- 1. CONFIGURAZIONE API ---
API_KEY = "ea1f03fb102749fa9140e20b184f2996" 
BASE_URL = "https://api.football-data.org/v4/"

# --- 2. DATABASE AVANZATO ---
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # Tabella completa v23
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, current_bet TEXT, 
                  theme TEXT, created_at TEXT, status TEXT DEFAULT 'active', 
                  warnings INTEGER DEFAULT 0, avatar TEXT)''')
    
    # Migrazioni automatiche per aggiornare vecchi database
    cols = [column[1] for column in c.execute("PRAGMA table_info(users)")]
    new_cols = {
        "theme": "TEXT DEFAULT '#3b82f6'",
        "created_at": "TEXT",
        "status": "TEXT DEFAULT 'active'",
        "warnings": "INTEGER DEFAULT 0",
        "avatar": "TEXT"
    }
    for col_name, col_type in new_cols.items():
        if col_name not in cols:
            c.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
            
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

# --- 3. UTILITY IMMAGINI & ANALISI ---
def img_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def get_deep_analysis():
    p = np.random.dirichlet(np.array([12, 6, 7]), size=1)[0]
    uo = random.uniform(0.3, 0.7)
    players = ["M. Rossi", "L. Moretti", "G. Esposito", "A. Ricci", "D. Bianchi"]
    reasons = ["Infortunio Muscolare", "Squalifica", "Problema Fisico"]
    return {
        "1X2": p, "UO25": [1-uo, uo],
        "RADAR": [random.randint(65, 98) for _ in range(5)],
        "h_abs": [{"n": random.choice(players), "r": random.choice(reasons)} for _ in range(random.randint(0,2))],
        "a_abs": [{"n": random.choice(players), "r": random.choice(reasons)} for _ in range(random.randint(0,2))],
        "ref": random.choice(["D. Orsato", "M. Oliver", "S. Marciniak"]),
        "wet": random.choice(["Sereno 22°C", "Pioggia 14°C", "Nuvoloso 18°C"])
    }

# --- 4. INIZIALIZZAZIONE SESSIONE ---
init_db()
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = ""
if 'schedina' not in st.session_state: st.session_state.schedina = []
if 'matches' not in st.session_state: st.session_state.matches = []
if 'theme_color' not in st.session_state: st.session_state.theme_color = "#3b82f6"
if 'avatar_b64' not in st.session_state: st.session_state.avatar_b64 = None
if 'last_selected' not in st.session_state: st.session_state.last_selected = None

# --- 5. UI & STILE LUXURY ---
st.set_page_config(page_title="NEURAL COMMANDER v23", layout="wide")
t_color = st.session_state.theme_color

st.markdown(f"""
    <style>
    header[data-testid="stHeader"] {{ visibility: hidden; }}
    .stApp {{ background-color: #030508; color: #e0e0e0; font-family: 'Inter', sans-serif; }}
    
    .data-card {{
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        border: 1px solid {t_color}33;
        border-radius: 24px; padding: 25px; margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
    }}
    
    .profile-pic {{
        width: 120px; height: 120px; border-radius: 50%;
        object-fit: cover; border: 3px solid {t_color};
        margin-bottom: 15px; box-shadow: 0 0 20px {t_color}55;
    }}

    .bet-row {{ 
        background: rgba(16, 185, 129, 0.08); border-radius: 15px; 
        padding: 15px; margin-bottom: 10px; border-left: 5px solid #10b981; 
    }}
    
    .terminal-text {{ font-family: 'Courier New', monospace; color: #10b981; font-size: 0.85rem; }}
    </style>
""", unsafe_allow_html=True)

# --- 6. GATEKEEPER (ACCESSO) ---
if not st.session_state.logged_in:
    st.markdown(f"<h1 style='text-align:center; color:{t_color};'>NEURAL COMMANDER</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        mode = st.radio("Accesso", ["Login", "Registrazione"], horizontal=True)
        u_in = st.text_input("Username")
        p_in = st.text_input("Password", type="password")
        
        if mode == "Login":
            if st.button("AUTENTICAZIONE", use_container_width=True):
                conn = sqlite3.connect('users.db'); c = conn.cursor()
                c.execute('SELECT password, current_bet, theme, avatar, status FROM users WHERE username = ?', (u_in,))
                data = c.fetchone(); conn.close()
                if data:
                    if data[4] == 'banned': st.error("🚫 ACCOUNT BANNATO")
                    elif data[0] == make_hashes(p_in):
                        st.session_state.logged_in = True
                        st.session_state.user = u_in
                        st.session_state.schedina = json.loads(data[1]) if data[1] else []
                        st.session_state.theme_color = data[2] if data[2] else "#3b82f6"
                        st.session_state.avatar_b64 = data[3]
                        st.rerun()
                    else: st.error("Password errata")
                else: st.error("Utente non trovato")
        else:
            if st.button("CREA PROFILO", use_container_width=True):
                if u_in and p_in:
                    conn = sqlite3.connect('users.db'); c = conn.cursor()
                    try:
                        c.execute('INSERT INTO users(username, password, created_at) VALUES (?,?,?)', 
                                  (u_in, make_hashes(p_in), datetime.now().strftime("%d/%m/%Y")))
                        conn.commit(); st.success("Registrato! Effettua il login.")
                    except: st.error("Username occupato")
                    conn.close()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 7. DASHBOARD OPERATIVA ---
else:
    tabs_list = ["🚀 ANALISI", "📝 SCHEDINA", "⚙️ ACCOUNT"]
    if st.session_state.user.lower() == "admin": tabs_list.append("🔐 ADMIN")
    
    t = st.tabs(tabs_list)

    # --- TAB ANALISI ---
    with t[0]:
        st.markdown(f"<p style='color:{t_color}'>Operatore: <b>{st.session_state.user}</b></p>", unsafe_allow_html=True)
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            league = st.selectbox("Lega", ["Serie A (SA)", "Premier League (PL)", "La Liga (PD)"])
            l_code = league.split("(")[1].replace(")", "")
        with c2:
            if st.button("🔄 SINCRONIZZA FEED", use_container_width=True):
                res = requests.get(f"{BASE_URL}competitions/{l_code}/matches?status=SCHEDULED", headers={'X-Auth-Token': API_KEY})
                if res.status_code == 200: st.session_state.matches = res.json().get('matches', [])
        
        matches = st.session_state.get('matches', [])
        if matches:
            labels = [f"{m['homeTeam']['name']} vs {m['awayTeam']['name']}" for m in matches]
            selected = st.selectbox("🎯 Seleziona Target", ["---"] + labels)
            if selected != "---":
                m_data = matches[labels.index(selected)]
                res = get_deep_analysis()
                st.markdown(f"<h3 style='text-align:center;'>{m_data['homeTeam']['name']} vs {m_data['awayTeam']['name']}</h3>", unsafe_allow_html=True)
                
                cl, cm, cr = st.columns([1, 1.5, 1])
                with cl:
                    st.markdown('<div class="data-card">', unsafe_allow_html=True)
                    st.write("🚑 **Assenti**")
                    for p in res['h_abs'] + res['a_abs']: st.write(f"• {p['n']}")
                    st.markdown('</div>', unsafe_allow_html=True)
                with cm:
                    st.markdown('<div class="data-card" style="text-align:center;">', unsafe_allow_html=True)
                    cols = st.columns(3)
                    for i, lab in enumerate(['1', 'X', '2']):
                        q = 1/res['1X2'][i]
                        if cols[i].button(f"{lab} @ {q:.2f}", key=f"b_{i}"):
                            st.session_state.schedina.append({"m": selected, "s": lab, "q": round(q, 2)})
                            save_bet_to_db(); st.toast("Aggiunto!")
                    st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB SCHEDINA ---
    with t[1]:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        if not st.session_state.schedina: st.info("Vuota.")
        else:
            total = 1.0
            for i, bet in enumerate(st.session_state.schedina):
                ci, cd = st.columns([5, 1])
                ci.markdown(f"<div class='bet-row'>{bet['m']} - {bet['s']} @ {bet['q']}</div>", unsafe_allow_html=True)
                if cd.button("🗑️", key=f"del_{i}"):
                    st.session_state.schedina.pop(i); save_bet_to_db(); st.rerun()
                total *= bet['q']
            st.metric("QUOTA", f"x {total:.2f}")
            if st.button("SVUOTA"): st.session_state.schedina = []; save_bet_to_db(); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB ACCOUNT & AVATAR ---
    with t[2]:
        col_p, col_i = st.columns([1, 2])
        with col_p:
            st.markdown('<div class="data-card" style="text-align:center;">', unsafe_allow_html=True)
            if st.session_state.avatar_b64:
                st.markdown(f'<img src="data:image/png;base64,{st.session_state.avatar_b64}" class="profile-pic">', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="width:120px; height:120px; background:{t_color}22; border-radius:50%; margin: 0 auto 15px; display:flex; align-items:center; justify-content:center; border:2px dashed {t_color};">?</div>', unsafe_allow_html=True)
            st.subheader(st.session_state.user)
            if st.button("🚪 LOGOUT", use_container_width=True, type="primary"):
                st.session_state.logged_in = False; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with col_i:
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            up = st.file_uploader("Carica Foto Profilo", type=["jpg", "png"])
            if up and st.button("SALVA FOTO"):
                b64 = img_to_base64(Image.open(up).resize((300, 300)))
                conn = sqlite3.connect('users.db'); c = conn.cursor()
                c.execute("UPDATE users SET avatar = ? WHERE username = ?", (b64, st.session_state.user))
                conn.commit(); conn.close(); st.session_state.avatar_b64 = b64; st.rerun()
            st.divider()
            new_c = st.color_picker("Colore Tema", t_color)
            if st.button("SALVA TEMA"):
                st.session_state.theme_color = new_c
                conn = sqlite3.connect('users.db'); c = conn.cursor()
                c.execute("UPDATE users SET theme = ? WHERE username = ?", (new_c, st.session_state.user))
                conn.commit(); conn.close(); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB ADMIN ---
    if st.session_state.user.lower() == "admin":
        with t[3]:
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            conn = sqlite3.connect('users.db')
            df = pd.read_sql_query("SELECT username, status, warnings FROM users", conn)
            for _, row in df.iterrows():
                if row['username'].lower() == 'admin': continue
                c_u, c_w, c_b = st.columns([2, 1, 1])
                c_u.write(f"**{row['username']}**")
                if c_w.button("⚠️ Warn", key=f"w_{row['username']}"):
                    conn.execute("UPDATE users SET warnings = warnings + 1 WHERE username = ?", (row['username'],))
                    conn.commit(); st.rerun()
                if c_b.button("🚫 Ban" if row['status']=='active' else "✅ Unban", key=f"b_{row['username']}"):
                    new_s = 'banned' if row['status']=='active' else 'active'
                    conn.execute("UPDATE users SET status = ? WHERE username = ?", (new_s, row['username']))
                    conn.commit(); st.rerun()
            conn.close()
            st.markdown('</div>', unsafe_allow_html=True)
