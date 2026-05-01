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

# --- 2. DATABASE AVANZATO ---
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    # Tabella utenti con stato (active/banned) e ammonizioni
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, current_bet TEXT, 
                  theme TEXT, created_at TEXT, status TEXT DEFAULT 'active', warnings INTEGER DEFAULT 0)''')
    
    # Migrazioni di sicurezza per colonne esistenti
    cols = [column[1] for column in c.execute("PRAGMA table_info(users)")]
    if "status" not in cols:
        c.execute("ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'active'")
    if "warnings" not in cols:
        c.execute("ALTER TABLE users ADD COLUMN warnings INTEGER DEFAULT 0")
    if "created_at" not in cols:
        c.execute("ALTER TABLE users ADD COLUMN created_at TEXT")
        
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
st.set_page_config(page_title="NEURAL COMMANDER v22", layout="wide")
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

# --- 6. ACCESSO (GATEKEEPER) ---
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
                c.execute('SELECT password, current_bet, theme, status FROM users WHERE username = ?', (u_in,))
                data = c.fetchone(); conn.close()
                if data:
                    if data[3] == 'banned':
                        st.error("🚫 ACCOUNT BANNATO. Contatta l'amministratore.")
                    elif data[0] == make_hashes(p_in):
                        st.session_state.logged_in = True
                        st.session_state.user = u_in
                        st.session_state.schedina = json.loads(data[1]) if data[1] else []
                        st.session_state.theme_color = data[2] if data[2] else "#3b82f6"
                        st.rerun()
                    else: st.error("Accesso Negato: password errata.")
                else: st.error("Utente non trovato.")
        else:
            if st.button("REGISTRATI", use_container_width=True):
                if u_in and p_in:
                    conn = sqlite3.connect('users.db'); c = conn.cursor()
                    now = datetime.now().strftime("%d/%m/%Y %H:%M")
                    try:
                        c.execute('INSERT INTO users(username, password, current_bet, theme, created_at, status, warnings) VALUES (?,?,?,?,?,?,?)', 
                                  (u_in, make_hashes(p_in), "[]", "#3b82f6", now, 'active', 0))
                        conn.commit(); st.success("Registrato con successo! Ora effettua il login.")
                    except: st.error("Errore: Username già occupato.")
                    conn.close()
        st.markdown('</div>', unsafe_allow_html=True)

# --- 7. AREA OPERATIVA ---
else:
    tabs_labels = ["🚀 ANALISI LIVE", "📝 LA MIA SCHEDINA", "⚙️ PROFILO"]
    if st.session_state.user.lower() == "admin": tabs_labels.append("🔐 ADMIN PANEL")
    
    t = st.tabs(tabs_labels)

    # --- TAB ANALISI ---
    with t[0]:
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
            selected = st.selectbox("🎯 Target", ["---"] + labels)
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
                    for i, lab in enumerate(['1', 'X', '2']):
                        q = 1/res['1X2'][i]
                        if cols[i].button(f"{lab} @ {q:.2f}", use_container_width=True, key=f"b_{i}"):
                            st.session_state.schedina.append({"m": selected, "s": lab, "q": round(q, 2)})
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
                    u, o = res['UO25']
                    if st.button(f"Over 2.5 @ {1/o:.2f}", use_container_width=True):
                        st.session_state.schedina.append({"m": selected, "s": "O2.5", "q": round(1/o, 2)})
                        save_bet_to_db(); st.toast("✅ Aggiunto!")
                    st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB SCHEDINA ---
    with t[1]:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.subheader("📝 Schedina Corrente")
        if not st.session_state.schedina: st.info("La tua schedina è vuota.")
        else:
            total = 1.0
            for i, bet in enumerate(st.session_state.schedina):
                ci, cd = st.columns([5, 1])
                ci.markdown(f"<div class='bet-row'>{bet['m']} - <b>{bet['s']}</b> @ {bet['q']}</div>", unsafe_allow_html=True)
                if cd.button("🗑️", key=f"del_{i}"):
                    st.session_state.schedina.pop(i); save_bet_to_db(); st.rerun()
                total *= bet['q']
            st.metric("MOLTIPLICATORE TOTALE", f"x {total:.2f}")
            if st.button("SVUOTA TUTTO", use_container_width=True):
                st.session_state.schedina = []; save_bet_to_db(); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB PROFILO ---
    with t[2]:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.subheader("👤 Gestione Profilo")
        new_user = st.text_input("Username", value=st.session_state.user)
        if st.button("Aggiorna Username"):
            conn = sqlite3.connect('users.db'); c = conn.cursor()
            try:
                c.execute("UPDATE users SET username = ? WHERE username = ?", (new_user, st.session_state.user))
                conn.commit(); st.session_state.user = new_user; st.success("Aggiornato!")
            except: st.error("Username occupato.")
            conn.close()
        
        st.divider()
        new_pass = st.text_input("Nuova Password", type="password")
        if st.button("Cambia Password"):
            if new_pass:
                conn = sqlite3.connect('users.db'); c = conn.cursor()
                c.execute("UPDATE users SET password = ? WHERE username = ?", (make_hashes(new_pass), st.session_state.user))
                conn.commit(); conn.close(); st.success("Password modificata!")

        st.divider()
        new_c = st.color_picker("Colore Tema", t_color)
        if st.button("Salva Tema"):
            st.session_state.theme_color = new_c
            conn = sqlite3.connect('users.db'); c = conn.cursor()
            c.execute("UPDATE users SET theme = ? WHERE username = ?", (new_c, st.session_state.user))
            conn.commit(); conn.close(); st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪 LOGOUT", use_container_width=True, type="primary"):
            st.session_state.logged_in = False; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TAB ADMIN (GESTIONE UTENTI) ---
    if st.session_state.user.lower() == "admin":
        with t[3]:
            st.markdown('<div class="data-card">', unsafe_allow_html=True)
            st.subheader("👥 Gestione Utenti Registrati")
            
            conn = sqlite3.connect('users.db')
            df = pd.read_sql_query("SELECT username, created_at, status, warnings FROM users", conn)
            
            for index, row in df.iterrows():
                if row['username'].lower() == 'admin': continue
                
                c_user, c_stat, c_warn, c_act = st.columns([2, 1, 1, 3.5])
                c_user.write(f"**{row['username']}**")
                c_stat.write(f"Stato: {row['status']}")
                c_warn.write(f"⚠️ {row['warnings']}")
                
                with c_act:
                    col_w, col_b, col_d = st.columns(3)
                    if col_w.button("⚠️ Warn", key=f"warn_{row['username']}"):
                        conn.execute("UPDATE users SET warnings = warnings + 1 WHERE username = ?", (row['username'],))
                        conn.commit(); st.rerun()
                    
                    if row['status'] == 'active':
                        if col_b.button("🚫 Ban", key=f"ban_{row['username']}"):
                            conn.execute("UPDATE users SET status = 'banned' WHERE username = ?", (row['username'],))
                            conn.commit(); st.rerun()
                    else:
                        if col_b.button("✅ Ok", key=f"unban_{row['username']}"):
                            conn.execute("UPDATE users SET status = 'active' WHERE username = ?", (row['username'],))
                            conn.commit(); st.rerun()
                            
                    if col_d.button("🗑️ Del", key=f"del_u_{row['username']}"):
                        conn.execute("DELETE FROM users WHERE username = ?", (row['username'],))
                        conn.commit(); st.rerun()
            
            conn.close()
            st.markdown('</div>', unsafe_allow_html=True)
