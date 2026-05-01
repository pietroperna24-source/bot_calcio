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
    # Tabella principale
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, current_bet TEXT, theme TEXT, created_at TEXT)''')
    # Migrazioni automatiche per colonne mancanti
    try:
        c.execute("ALTER TABLE users ADD COLUMN theme TEXT DEFAULT '#3b82f6'")
    except sqlite3.OperationalError: pass
    try:
        c.execute("ALTER TABLE users ADD COLUMN created_at TEXT")
    except sqlite3.OperationalError: pass
    
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

# --- 3. LOGICA DI ANALISI ---
def get_deep_analysis():
    p = np.random.dirichlet(np.array([12, 6, 7]), size=1)[0]
    uo = random.uniform(0.3, 0.7)
    gg = random.uniform(0.4, 0.6)
    players = ["M. Rossi", "L. Moretti", "G. Esposito", "A. Ricci", "D. Bianchi"]
    reasons = ["Infortunio Muscolare", "Squalifica", "Problema Fisico", "Scelta Tecnica"]
    return {
        "1X2": p, "UO25": [1-uo, uo], "GGNG": [gg, 1-gg],
        "RADAR": [random.randint(65, 98) for _ in range(5)],
        "h_abs": [{"n": random.choice(players), "r": random.choice(reasons)} for _ in range(random.randint(0,2))],
        "a_abs": [{"n": random.choice(players), "r": random.choice(reasons)} for _ in range(random.randint(0,2))],
        "ref": random.choice(["D. Orsato", "M. Oliver", "S. Marciniak"]),
        "wet": random.choice(["Sereno 22°C", "Pioggia 14°C", "Nuvoloso 18°C"])
    }

# --- 4. INIZIALIZZAZIONE ---
init_db()
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = ""
if 'schedina' not in st.session_state: st.session_state.schedina = []
if 'matches' not in st.session_state: st.session_state.matches = []
if 'theme_color' not in st.session_state: st.session_state.theme_color = "#3b82f6"
if 'last_selected' not in st.session_state: st.session_state.last_selected = None

# --- 5. UI & STILE ---
st.set_page_config(page_title="NEURAL COMMANDER v21.5", layout="wide")
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
    .bet-row {{ background: rgba(16, 185, 129, 0.05); border-radius: 10px; padding: 10px; margin-bottom: 8px; border-left: 4px solid #10b981; }}
    .absent-card {{ background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.2); padding: 8px; border-radius: 10px; margin-top: 5px; font-size: 0.8rem; }}
    .terminal-text {{ font-family: 'Courier New', monospace; color: #10b981; font-size: 0.85rem; }}
    </style>
""", unsafe_allow_html=True)

# --- 6. LOGICA ACCESSO (GATEKEEPER) ---
if not st.session_state.logged_in:
    st.markdown(f"<h1 style='text-align:center; color:{t_color};'>🛡️ NEURAL COMMANDER ACCESS</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        mode = st.radio("Azione", ["Login", "Registrazione"], horizontal=True)
        u_in = st.text_input("Username")
        p_in = st.text_input("Password", type="password")
        
        if mode == "Login":
            if st.button("ACCEDI", use_container_width=True):
                conn = sqlite3.connect('users.db'); c = conn.cursor()
                c.execute('SELECT password, current_bet, theme FROM users WHERE username = ?', (u_in,))
                data = c.fetchone(); conn.close()
                if data and data[0] == make_hashes(p_in):
                    st.session_state.logged_in = True
                    st.session_state.user = u_in
                    st.session_state.schedina = json.loads(data[1]) if data[1] else []
                    st.session_state.theme_color = data[2] if data[2] else "#3b82f6"
                    st.rerun()
                else: st.error("Accesso Negato.")
        else:
            if st.button("REGISTRATI", use_container_width=True):
                if u_in and p_in:
                    conn = sqlite3.connect('users.db'); c = conn.cursor()
                    now = datetime.now().strftime("%d/%m/%Y %H:%M")
                    try:
                        c.execute('INSERT INTO users(username, password, current_bet, theme, created_at) VALUES (?,?,?,?,?)', 
                                  (u_in, make_hashes(p_in), "[]", "#3b82f6", now))
                        conn.commit(); st.success("Registrato! Ora effettua il login.")
                    except: st.error("Errore: Username già occupato.")
                    conn.close()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 7. AREA OPERATIVA ---
else:
    # Gestione dinamica dei Tab (Aggiunge Admin se l'utente è "admin")
    tabs_list = ["🚀 ANALISI LIVE", "📝 LA MIA SCHEDINA", "⚙️ IMPOSTAZIONI"]
    if st.session_state.user.lower() == "admin":
        tabs_list.append("🔐 PANNELLO ADMIN")
    
    t_analisi, t_schedina, t_settings, *t_admin = st.tabs(tabs_list)

    # --- TAB ANALISI ---
    with t_analisi:
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
            labels = [f"{datetime.fromisoformat(m['utcDate'].replace('Z', '+00:00')).strftime('%H:%M')} | {m['homeTeam']['name']} vs {m['awayTeam']['name']}" for m in matches]
            selected = st.selectbox("🎯 Seleziona Target", ["---"] + labels)
            
            if selected != "---":
                if st.session_state.last_selected != selected:
                    ph = st.empty()
                    with ph.container():
                        st.markdown('<div class="data-card">', unsafe_allow_html=True)
                        st.markdown("<p class='terminal-text'>[SCAN]: Avvio Scansione Neurale...</p>", unsafe_allow_html=True)
                        pb = st.progress(0)
                        for i, step in enumerate(["📡 Link API...", "🧬 Power Index...", "🚑 Infermeria...", "✅ Pronto."]):
                            time.sleep(0.3); st.markdown(f"<p class='terminal-text' style='opacity:0.7;'>{step}</p>", unsafe_allow_html=True)
                            pb.progress((i+1)*25)
                        st.markdown('</div>', unsafe_allow_html=True)
                    ph.empty(); st.session_state.last_selected = selected

                m_data = matches[labels.index(selected)]
                h_n, a_n = m_data['homeTeam']['name'], m_data['awayTeam']['name']
                res = get_deep_analysis()

                st.markdown(f"<h3 style='text-align:center;'>{h_n.upper()} vs {a_n.upper()}</h3>", unsafe_allow_html=True)
                
                cl, cm, cr = st.columns([1, 1.5, 1])
                with cl:
                    st.markdown('<div class="data-card">', unsafe_allow_html=True)
                    st.write("🚑 **Assenti Home**")
                    if not res['h_abs']: st.write("✅ Nessuno")
                    for p in res['h_abs']: st.markdown(f"<div class='absent-card'><b>{p['n']}</b><br>{p['r']}</div>", unsafe_allow_html=True)
                    st.divider()
                    st.write(f"⚖️ {res['ref']}")
                    st.write(f"☁️ {res['wet']}")
                    st.markdown('</div>', unsafe_allow_html=True)

                with cm:
                    st.markdown('<div class="data-card" style="text-align:center;">', unsafe_allow_html=True)
                    st.subheader("🎯 Neural Probabilities")
                    cols = st.columns(3)
                    labs = ['1', 'X', '2']
                    for i, col in enumerate(cols):
                        q = 1/res['1X2'][i]
                        if col.button(f"{labs[i]} @ {q:.2f}", use_container_width=True, key=f"bet_{i}"):
                            st.session_state.schedina.append({"m": f"{h_n}-{a_n}", "s": labs[i], "q": q})
                            save_bet_to_db(); st.toast("✅ Aggiunto!")
                    
                    fig = go.Figure(data=go.Scatterpolar(r=res['RADAR'], theta=['Att','Dif','For','Fis','Tat'], fill='toself', line_color=t_color))
                    fig.update_layout(polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(visible=False, range=[0, 100])), showlegend=False, height=200, margin=dict(t=20,b=20,l=35,r=35), paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                with cr:
                    st.markdown('<div class="data-card">', unsafe_allow_html=True)
                    st.write("🚑 **Assenti Away**")
                    if not res['a_abs']: st.write("✅ Nessuno")
                    for p in res['a_abs']: st.markdown(f"<div class='absent-card'><b>{p['n']}</b><br>{p['r']}</div>", unsafe_allow_html=True)
                    st.divider()
                    st.write("⚽ **Extra Markets**")
                    u, o = res['UO25']
                    if st.button(f"Over 2.5 @ {1/o:.2f}", use_container_width=True):
                        st.session_state.schedina.append({"m": f"{h_n}-{a_n}", "s": "Over 2.5", "q": 1/o})
                        save_bet_to_db(); st.toast("✅ Over Aggiunto!")
                    st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB SCHEDINA ---
    with t_schedina:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.subheader("📋 Schedina Salvata")
        if not st.session_state.schedina: st.info("Sposta qui i tuoi pronostici cliccando sulle quote.")
        else:
            total = 1.0
            for i, bet in enumerate(st.session_state.schedina):
                c_i, c_d = st.columns([5, 1])
                c_i.markdown(f"<div class='bet-row'>{bet['m']} - <b>{bet['s']}</b> @ {bet['q']:.2f}</div>", unsafe_allow_html=True)
                if c_d.button("🗑️", key=f"del_{i}"):
                    st.session_state.schedina.pop(i); save_bet_to_db(); st.rerun()
                total *= bet['q']
            st.metric("QUOTA TOTALE", f"x {total:.2f}")
            if st.button("🗑️ SVUOTA TUTTO", use_container_width=True):
                st.session_state.schedina = []; save_bet_to_db(); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB IMPOSTAZIONI ---
    with t_settings:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.subheader("⚙️ Gestione Profilo")
        # Username
        new_user = st.text_input("Modifica Username", value=st.session_state.user)
        if st.button("Aggiorna Username"):
            conn = sqlite3.connect('users.db'); c = conn.cursor()
            try:
                c.execute("UPDATE users SET username = ? WHERE username = ?", (new_user, st.session_state.user))
                conn.commit(); st.session_state.user = new_user; st.success("Username Aggiornato!")
            except: st.error("Errore: Nome già occupato.")
            conn.close()
        st.divider()
        # Password
        new_pass = st.text_input("Nuova Password", type="password")
        if st.button("Aggiorna Password"):
            if new_pass:
                conn = sqlite3.connect('users.db'); c = conn.cursor()
                c.execute("UPDATE users SET password = ? WHERE username = ?", (make_hashes(new_pass), st.session_state.user))
                conn.commit(); conn.close(); st.success("Password Cambiata!")
        st.divider()
        # Tema
        new_c = st.color_picker("Colore Tema", t_color)
        if st.button("Salva Colore"):
            st.session_state.theme_color = new_c
            conn = sqlite3.connect('users.db'); c = conn.cursor()
            c.execute("UPDATE users SET theme = ? WHERE username = ?", (new_c, st.session_state.user))
            conn.commit(); conn.close(); st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 LOGOUT", use_container_width=True, type="primary"):
            st.session_state.logged_in = False; st.session_state.user = ""; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB ADMIN (Solo se Admin) ---
    if st.session_state.user.lower() == "admin":
        with t_admin[0]:
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            st.subheader("👥 Registro Utenti Registrati")
            conn = sqlite3.connect('users.db')
            df = pd.read_sql_query("SELECT username, created_at, theme FROM users", conn)
            conn.close()
            st.write(f"Totale Utenti Iscritti: **{len(df)}**")
            st.dataframe(df, use_container_width=True)
            if st.button("Aggiorna Database"): st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
