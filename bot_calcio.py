import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. DATABASE SQUADRE (POWER INDEX) ---
TEAMS_DB = {
    "Italia - Serie A": {
        "Inter": 91, "Milan": 85, "Juventus": 84, "Napoli": 82, "Atalanta": 83, 
        "Roma": 79, "Lazio": 78, "Fiorentina": 77, "Bologna": 78, "Torino": 74
    },
    "Inghilterra - Premier League": {
        "Man City": 96, "Arsenal": 93, "Liverpool": 94, "Man United": 81, "Chelsea": 80
    }
}

# --- 2. DATABASE PARTITE (Con Risultati per Archivio) ---
# Se 'risultato' è None, la partita è in programma. Se c'è (es. "2-1"), è conclusa.
if 'history' not in st.session_state:
    st.session_state.history = [
        {"data": "2026-05-01", "lega": "Italia - Serie A", "home": "Juventus", "away": "Torino", "risultato": "1-0"},
        {"data": "2026-05-02", "lega": "Italia - Serie A", "home": "Inter", "away": "Milan", "risultato": None},
        {"data": "2026-05-02", "lega": "Inghilterra - Premier League", "home": "Arsenal", "away": "Liverpool", "risultato": None},
    ]

# --- 3. MOTORE ANALITICO AVANZATO ---
def analyze_full(home, away, lega):
    db = TEAMS_DB.get(lega, {})
    ph = db.get(home, 75)
    pa = db.get(away, 75)
    
    # Calcolo 1X2
    total = (ph * 1.10) + pa # +10% vantaggio casa
    p1 = (ph * 1.10) / total * 0.75
    p2 = pa / total * 0.75
    px = 1.0 - (p1 + p2)
    
    # Calcolo Under/Over 2.5 (Semplificato su Power Index totale)
    uo_factor = (ph + pa) / 200
    p_over = uo_factor * 1.2 if uo_factor > 0.8 else uo_factor 
    
    return {
        "1X2": [p1, px, p2],
        "UO25": [1-p_over, p_over], # Under, Over
        "score_pred": f"{int((ph/pa)*1.2)}-{int((pa/ph)*1.1)}"
    }

# --- 4. INTERFACCIA ---
st.set_page_config(page_title="AI FOOTBALL PRO", layout="wide")

st.markdown("""
    <style>
    #MainMenu, header, footer {visibility: hidden; display: none !important;}
    .stApp { background: #0b0e14; }
    .card { background: #161b22; border-radius: 12px; padding: 20px; border: 1px solid #30363d; margin-bottom: 15px; }
    .win { border-left: 5px solid #22c55e; }
    .pending { border-left: 5px solid #3b82f6; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏆 AI Football Management System")

tab_cat, tab_arch, tab_input = st.tabs(["📅 Catalogo Odierno", "📚 Archivio Risultati", "➕ Gestione Palinsesto"])

# --- TAB 1: CATALOGO ---
with tab_cat:
    st.subheader("Partite in Programma")
    pending = [m for m in st.session_state.history if m['risultato'] is None]
    
    for m in pending:
        res = analyze_full(m['home'], m['away'], m['lega'])
        with st.container():
            st.markdown(f'<div class="card pending">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.write(f"**{m['lega']}**")
                st.write(f"### {m['home']} vs {m['away']}")
                st.write(f"🔮 Risultato Esatto AI: **{res['score_pred']}**")
            with col2:
                # Percentuali
                cols_p = st.columns(3)
                cols_p[0].metric("1", f"{res['1X2'][0]:.0%}")
                cols_p[1].metric("X", f"{res['1X2'][1]:.0%}")
                cols_p[2].metric("2", f"{res['1X2'][2]:.0%}")
                st.progress(res['UO25'][1], text=f"Probabilità Over 2.5: {res['UO25'][1]:.0%}")
            with col3:
                st.write("🎯 **Suggerimento**")
                if res['1X2'][0] > 0.50: st.success("Punta 1")
                elif res['1X2'][2] > 0.50: st.error("Punta 2")
                else: st.warning("Punta X o Goal")
            st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 2: ARCHIVIO ---
with tab_arch:
    st.subheader("Storico Partite Concluse")
    concluded = [m for m in st.session_state.history if m['risultato'] is not None]
    if concluded:
        df = pd.DataFrame(concluded)
        st.table(df)
    else:
        st.write("Nessuna partita archiviata.")

# --- TAB 3: GESTIONE ---
with tab_input:
    st.subheader("Inserisci Nuove Partite o Risultati")
    with st.expander("Aggiungi Match"):
        c1, c2, c3, c4 = st.columns(4)
        lega = c1.selectbox("Lega", list(TEAMS_DB.keys()))
        h = c2.selectbox("Casa", list(TEAMS_DB[lega].keys()))
        a = c3.selectbox("Trasferta", list(TEAMS_DB[lega].keys()))
        d = c4.date_input("Data")
        if st.button("Aggiungi al Catalogo"):
            st.session_state.history.append({"data": str(d), "lega": lega, "home": h, "away": a, "risultato": None})
            st.rerun()
            
    with st.expander("Inserisci Risultato"):
        match_to_close = st.selectbox("Seleziona match concluso", [f"{m['home']}-{m['away']}" for m in pending])
        score = st.text_input("Risultato Finale (es. 2-1)")
        if st.button("Aggiorna Risultato"):
            for m in st.session_state.history:
                if f"{m['home']}-{m['away']}" == match_to_close:
                    m['risultato'] = score
            st.rerun()
