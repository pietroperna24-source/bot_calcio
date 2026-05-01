import streamlit as st
import time
import random
import plotly.graph_objects as go
from datetime import datetime

# --- 1. DATABASE INTEGRALE EUROPA 2026 (98 SQUADRE) ---
EURO_DB = {
    "Serie A 🇮🇹": {
        "Atalanta": {"pw": 86, "miss": ["Scamacca (I)"], "f": "WWWLD", "style": [9,6,8,7,9], "color": "#00539c"},
        "Bologna": {"pw": 79, "miss": [], "f": "DDWLW", "style": [7,7,8,6,7], "color": "#a7171a"},
        "Cagliari": {"pw": 71, "miss": [], "f": "LLDDW", "style": [5,8,5,8,6], "color": "#002350"},
        "Como": {"pw": 76, "miss": ["Varane (I)"], "f": "WLDLW", "style": [7,6,8,6,7], "color": "#003399"},
        "Empoli": {"pw": 70, "miss": [], "f": "LDDWL", "style": [5,8,6,7,5], "color": "#005baa"},
        "Fiorentina": {"pw": 81, "miss": [], "f": "WWDLD", "style": [8,6,8,6,7], "color": "#4b2e83"},
        "Genoa": {"pw": 76, "miss": [], "f": "DWLLW", "style": [6,7,6,8,7], "color": "#a7171a"},
        "Inter": {"pw": 94, "miss": ["Barella (S)"], "f": "WWWDW", "style": [9,8,9,7,9], "color": "#006294"},
        "Juventus": {"pw": 88, "miss": ["Nico Gonzalez (I)"], "f": "WWDDW", "style": [6,9,7,9,6], "color": "#ffffff"},
        "Lazio": {"pw": 82, "miss": [], "f": "LWLDW", "style": [7,6,7,7,8], "color": "#87d3f8"},
        "Lecce": {"pw": 72, "miss": [], "f": "LLDWL", "style": [6,7,5,8,7], "color": "#ffed00"},
        "Milan": {"pw": 88, "miss": ["Maignan (I)"], "f": "WDLWW", "style": [8,7,8,8,7], "color": "#fb1107"},
        "Monza": {"pw": 74, "miss": [], "f": "LDDWW", "style": [6,7,7,6,6], "color": "#e30613"},
        "Napoli": {"pw": 87, "miss": ["Osimhen (N)"], "f": "LWWLD", "style": [8,7,9,6,8], "color": "#0091ff"},
        "Parma": {"pw": 74, "miss": [], "f": "WLDDL", "style": [7,6,6,7,8], "color": "#fff200"},
        "Roma": {"pw": 83, "miss": ["Dybala (I)"], "f": "DDWLW", "style": [7,7,8,7,7], "color": "#8e001c"},
        "Torino": {"pw": 77, "miss": ["Zapata (I)"], "f": "LLWDW", "style": [6,8,6,9,7], "color": "#8a1e19"},
        "Udinese": {"pw": 74, "miss": [], "f": "WLDDW", "style": [6,8,6,8,7], "color": "#ffffff"},
        "Venezia": {"pw": 69, "miss": [], "f": "LLLWD", "style": [6,6,7,6,7], "color": "#00633c"},
        "Verona": {"pw": 71, "miss": [], "f": "WLLDL", "style": [5,7,6,8,7], "color": "#00357d"}
    },
    "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": {
        "Arsenal": {"pw": 95, "miss": ["Odegaard (I)"], "f": "WWWLW", "style": [9,9,9,8,8], "color": "#ef0107"},
        "Aston Villa": {"pw": 86, "miss": [], "f": "WWDWL", "style": [8,7,8,8,8], "color": "#95bfe5"},
        "Chelsea": {"pw": 85, "miss": ["James (I)"], "f": "LDWWW", "style": [8,6,8,6,8], "color": "#034694"},
        "Liverpool": {"pw": 94, "miss": ["Alisson (I)"], "f": "WWDWW", "style": [10,7,10,6,10], "color": "#e31b23"},
        "Man City": {"pw": 97, "miss": ["Rodri (I)"], "f": "WWWWW", "style": [10,8,10,7,9], "color": "#6caee0"},
        "Man United": {"pw": 83, "miss": ["Shaw (I)"], "f": "WLLDW", "style": [8,6,8,6,8], "color": "#da291c"},
        "Tottenham": {"pw": 86, "miss": ["Son (I)"], "f": "DWLWW", "style": [9,6,8,6,10], "color": "#132257"}
    },
    "La Liga 🇪🇸": {
        "Atletico Madrid": {"pw": 90, "miss": ["De Paul (I)"], "f": "WWDLD", "style": [7,10,7,10,7], "color": "#cb3524"},
        "Barcelona": {"pw": 94, "miss": ["Gavi (I)"], "f": "WWWLW", "style": [9,6,10,6,8], "color": "#a50044"},
        "Real Madrid": {"pw": 98, "miss": ["Courtois (I)"], "f": "WWWWD", "style": [10,8,9,8,10], "color": "#ffffff"},
        "Girona": {"pw": 84, "miss": [], "f": "LWWDL", "style": [9,6,9,6,8], "color": "#e2362c"},
        "Real Sociedad": {"pw": 83, "miss": [], "f": "LDWWD", "style": [7,8,9,7,7], "color": "#0067b1"}
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

# --- 3. UI LAYOUT & CSS ---
st.set_page_config(page_title="AI NEURAL COMMANDER", layout="wide")

st.markdown("""
    <style>
    /* Nasconde header e footer senza bloccare la sidebar */
    header[data-testid="stHeader"] { visibility: hidden; height: 0px; }
    footer { visibility: hidden; }
    
    /* Etichetta fissa in alto a destra */
    .custom-label {
        position: fixed;
        top: 10px;
        right: 20px;
        z-index: 1000;
        color: #3b82f6;
        background: rgba(15, 23, 42, 0.8);
        padding: 5px 15px;
        border: 1px solid #3b82f6;
        border-radius: 8px;
        font-family: sans-serif;
        font-weight: bold;
        font-size: 12px;
        letter-spacing: 1px;
    }

    .stApp { background-color: #05070a; color: #e0e0e0; }
    .vs-text { font-size: 3.5rem; font-weight: 900; color: #3b82f6; text-align: center; margin-top: 10px; }
    .block-container { padding-top: 2rem; }
    </style>
    <div class="custom-label">📂 CATALOGO ATTIVO</div>
""", unsafe_allow_html=True)

# --- 4. SIDEBAR (CATALOGO) ---
with st.sidebar:
    st.title("📂 CATALOGO")
    st.markdown("---")
    sel_league = st.selectbox("Campionato", list(EURO_DB.keys()))
    
    st.subheader("🎮 Match Control")
    teams = sorted(list(EURO_DB[sel_league].keys()))
    h_team = st.selectbox("Casa", teams, index=0)
    a_team = st.selectbox("Trasferta", teams, index=1 if len(teams) > 1 else 0)
    
    st.divider()
    analyze_btn = st.button("🔥 GENERA REPORT", use_container_width=True)

# --- 5. MAIN LOGIC ---
st.title("⚡ AI NEURAL COMMANDER 2026")

if analyze_btn:
    if h_team == a_team:
        st.error("Seleziona squadre diverse.")
    else:
        with st.status("🧬 Analisi in corso...", expanded=True) as status:
            time.sleep(0.5); st.write("📥 Accesso database..."); time.sleep(0.5)
            status.update(label="Analisi Completata!", state="complete")

        probs, hh, ha = get_analysis(h_team, a_team, sel_league)
        sh, sa = EURO_DB[sel_league][h_team], EURO_DB[sel_league][a_team]

        st.markdown(f"<div class='vs-text'>{h_team.upper()} <small>vs</small> {a_team.upper()}</div>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1, 2, 1])

        with c1:
            st.subheader(f"🏠 {h_team}")
            st.progress(hh/100, text=f"Integrità: {hh}%")
            fig_r1 = go.Figure(data=go.Scatterpolar(r=sh['style'], theta=['Att','Dif','Pos','Fis','Vel'], fill='toself', line_color=sh['color']))
            fig_r1.update_layout(polar=dict(bgcolor='#0f172a', radialaxis=dict(visible=False, range=[0, 10])), showlegend=False, height=250, margin=dict(t=30,b=30,l=30,r=30))
            st.plotly_chart(fig_r1, use_container_width=True)

        with c2:
            st.subheader("🎯 Probabilità")
            fig_pie = go.Figure(go.Pie(labels=['1', 'X', '2'], values=probs, hole=.7, marker_colors=[sh['color'], '#222', sa['color']]))
            fig_pie.update_layout(showlegend=False, height=350, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_pie, use_container_width=True)
            st.metric("FIDUCIA AI", f"{max(probs)*100:.1f}%")

        with c3:
            st.subheader(f"🚌 {a_team}")
            st.progress(ha/100, text=f"Integrità: {ha}%")
            fig_r2 = go.Figure(data=go.Scatterpolar(r=sa['style'], theta=['Att','Dif','Pos','Fis','Vel'], fill='toself', line_color=sa['color']))
            fig_r2.update_layout(polar=dict(bgcolor='#0f172a', radialaxis=dict(visible=False, range=[0, 10])), showlegend=False, height=250, margin=dict(t=30,b=30,l=30,r=30))
            st.plotly_chart(fig_r2, use_container_width=True)
            
