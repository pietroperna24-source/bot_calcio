import streamlit as st
import time
import random
import plotly.graph_objects as go
from datetime import datetime

# --- 1. DATABASE (Estratto per brevità) ---
EURO_DB = {
    "Serie A 🇮🇹": {
        "Inter": {"pw": 94, "miss": ["Barella (S)"], "f": "WWWDW", "style": [9,8,9,7,9], "color": "#006294"},
        "Juventus": {"pw": 88, "miss": ["Nico Gonzalez (I)"], "f": "WWDDW", "style": [6,9,7,9,6], "color": "#ffffff"},
        "Milan": {"pw": 88, "miss": ["Maignan (I)"], "f": "WDLWW", "style": [8,7,8,8,7], "color": "#fb1107"},
        "Napoli": {"pw": 87, "miss": ["Osimhen (N)"], "f": "LWWLD", "style": [8,7,9,6,8], "color": "#0091ff"},
    }
}

# --- 2. ENGINE ANALITICO ---
def get_analysis(h, a, league):
    sh, sa = EURO_DB[league][h], EURO_DB[league][a]
    health_h = max(10, 100 - (len(sh['miss']) * 15))
    health_a = max(10, 100 - (len(sa['miss']) * 15))
    pw_h = (sh['pw'] * (health_h/100)) + 5
    pw_a = (sa['pw'] * (health_a/100))
    total = pw_h + pw_a + 25
    probs = [pw_h/total, 25/total, pw_a/total]
    return probs, health_h, health_a

# --- 3. UI LAYOUT & CSS PERSONALIZZATO ---
st.set_page_config(page_title="AI NEURAL COMMANDER", layout="wide")

st.markdown("""
    <style>
    /* 1. Nasconde l'header originale */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    
    /* 2. Nasconde il footer */
    footer {visibility: hidden;}

    /* 3. Posizionamento "Catalogo" in alto a destra */
    .custom-nav-label {
        position: fixed;
        top: 15px;
        right: 25px;
        z-index: 9999;
        font-family: 'Source Sans Pro', sans-serif;
        font-weight: 700;
        color: #3b82f6;
        background: rgba(30, 41, 59, 0.7);
        padding: 5px 15px;
        border-radius: 10px;
        border: 1px solid #3b82f6;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stApp { background-color: #05070a; color: #e0e0e0; }
    .vs-text { font-size: 3.5rem; font-weight: 900; color: #3b82f6; text-align: center; margin-top: 10px; }
    
    .block-container {
        padding-top: 2rem;
    }
    </style>
    
    <!-- Elemento iniettato in alto a destra -->
    <div class="custom-nav-label">📂 Catalogo Attivo</div>
""", unsafe_allow_html=True)

st.title("⚡ AI NEURAL COMMANDER 2026")
st.caption("Database Integrale: Top Campionati Europei")

# --- SIDEBAR ---
with st.sidebar:
    st.header("📂 GESTIONE DATI")
    sel_league = st.selectbox("Seleziona Campionato", list(EURO_DB.keys()))
    st.divider()
    st.subheader("🎮 Match Control")
    teams = sorted(list(EURO_DB[sel_league].keys()))
    h_team = st.selectbox("Squadra in Casa", teams, index=0)
    a_team = st.selectbox("Squadra in Trasferta", teams, index=1 if len(teams) > 1 else 0)
    st.divider()
    analyze_btn = st.button("🔥 GENERA REPORT NEURALE", use_container_width=True)

# --- LOGICA PRINCIPALE ---
if analyze_btn:
    if h_team == a_team:
        st.error("Seleziona squadre diverse.")
    else:
        with st.status("🧬 Elaborazione dati...", expanded=True) as status:
            time.sleep(0.5); st.write("📥 Caricamento database..."); time.sleep(0.5)
            status.update(label="Analisi Completata!", state="complete")

        probs, hh, ha = get_analysis(h_team, a_team, sel_league)
        sh, sa = EURO_DB[sel_league][h_team], EURO_DB[sel_league][a_team]

        st.markdown(f"<div class='vs-text'>{h_team.upper()} <small>vs</small> {a_team.upper()}</div>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1, 2, 1])

        with c1:
            st.subheader(f"🏠 {h_team}")
            st.progress(hh/100, text=f"Health: {hh}%")
            fig_r1 = go.Figure(data=go.Scatterpolar(r=sh['style'], theta=['Att','Dif','Pos','Fis','Vel'], fill='toself', line_color=sh['color']))
            fig_r1.update_layout(polar=dict(bgcolor='#0f172a', radialaxis=dict(visible=False, range=[0, 10])), showlegend=False, height=250, margin=dict(t=30,b=30,l=30,r=30))
            st.plotly_chart(fig_r1, use_container_width=True)

        with c2:
            st.subheader("🎯 Esito Probabile")
            fig_pie = go.Figure(go.Pie(labels=['1', 'X', '2'], values=probs, hole=.7, marker_colors=[sh['color'], '#222', sa['color']]))
            fig_pie.update_layout(showlegend=False, height=350, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_pie, use_container_width=True)
            st.metric("FIDUCIA AI", f"{max(probs)*100:.1f}%")

        with c3:
            st.subheader(f"🚌 {a_team}")
            st.progress(ha/100, text=f"Health: {ha}%")
            fig_r2 = go.Figure(data=go.Scatterpolar(r=sa['style'], theta=['Att','Dif','Pos','Fis','Vel'], fill='toself', line_color=sa['color']))
            fig_r2.update_layout(polar=dict(bgcolor='#0f172a', radialaxis=dict(visible=False, range=[0, 10])), showlegend=False, height=250, margin=dict(t=30,b=30,l=30,r=30))
            st.plotly_chart(fig_r2, use_container_width=True)
            
