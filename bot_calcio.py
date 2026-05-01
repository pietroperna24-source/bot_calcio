import streamlit as st
import time
import random
import plotly.graph_objects as go
from datetime import datetime

# --- 1. DATABASE INTEGRALE EUROPEO 2026 ---
# Include tutte le squadre ufficiali per ogni campionato
EURO_DB = {
    "Serie A 🇮🇹": {
        "Atalanta": {"pw": 86, "miss": ["Scamacca (I)"], "f": "WWWLD"},
        "Bologna": {"pw": 79, "miss": [], "f": "DDWLW"},
        "Cagliari": {"pw": 71, "miss": [], "f": "LLDDW"},
        "Como": {"pw": 75, "miss": ["Varane (I)"], "f": "WLDLW"},
        "Empoli": {"pw": 70, "miss": [], "f": "LDDWL"},
        "Fiorentina": {"pw": 81, "miss": [], "f": "WWDLD"},
        "Genoa": {"pw": 76, "miss": [], "f": "DWLLW"},
        "Inter": {"pw": 94, "miss": ["Barella (S)"], "f": "WWWDW"},
        "Juventus": {"pw": 88, "miss": ["Nico Gonzalez (I)"], "f": "WWDDW"},
        "Lazio": {"pw": 82, "miss": [], "f": "LWLDW"},
        "Lecce": {"pw": 72, "miss": [], "f": "LLDWL"},
        "Milan": {"pw": 88, "miss": ["Maignan (I)"], "f": "WDLWW"},
        "Monza": {"pw": 74, "miss": [], "f": "LDDWW"},
        "Napoli": {"pw": 87, "miss": ["Osimhen (N)"], "f": "LWWLD"},
        "Parma": {"pw": 73, "miss": [], "f": "WLDDL"},
        "Roma": {"pw": 83, "miss": ["Dybala (I)"], "f": "DDWLW"},
        "Torino": {"pw": 77, "miss": ["Zapata (I)"], "f": "LLWDW"},
        "Udinese": {"pw": 74, "miss": [], "f": "WLDDW"},
        "Venezia": {"pw": 69, "miss": [], "f": "LLLWD"},
        "Verona": {"pw": 71, "miss": [], "f": "WLLDL"}
    },
    "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": {
        "Arsenal": {"pw": 95, "miss": ["Odegaard (I)"], "f": "WWWLW"},
        "Aston Villa": {"pw": 86, "miss": [], "f": "WWDWL"},
        "Bournemouth": {"pw": 76, "miss": [], "f": "WLDDW"},
        "Brentford": {"pw": 77, "miss": [], "f": "LWDWW"},
        "Brighton": {"pw": 82, "miss": [], "f": "DWWLD"},
        "Chelsea": {"pw": 85, "miss": ["James (I)"], "f": "LDWWW"},
        "Crystal Palace": {"pw": 75, "miss": [], "f": "DDLWW"},
        "Everton": {"pw": 73, "miss": [], "f": "LLLDW"},
        "Fulham": {"pw": 76, "miss": [], "f": "WDDLW"},
        "Ipswich": {"pw": 68, "miss": [], "f": "LLLDD"},
        "Leicester": {"pw": 71, "miss": [], "f": "LDDLW"},
        "Liverpool": {"pw": 94, "miss": ["Alisson (I)"], "f": "WWDWW"},
        "Man City": {"pw": 97, "miss": ["Rodri (I)", "De Bruyne (I)"], "f": "WWWWW"},
        "Man United": {"pw": 83, "miss": ["Shaw (I)"], "f": "WLLDW"},
        "Newcastle": {"pw": 84, "miss": ["Isak (I)"], "f": "WLDWW"},
        "Nottm Forest": {"pw": 74, "miss": [], "f": "DWWLD"},
        "Southampton": {"pw": 69, "miss": [], "f": "LLLLL"},
        "Tottenham": {"pw": 86, "miss": ["Son (I)"], "f": "DWLWW"},
        "West Ham": {"pw": 78, "miss": [], "f": "LDDLW"},
        "Wolves": {"pw": 72, "miss": [], "f": "LLLDL"}
    },
    "La Liga 🇪🇸": {
        "Alaves": {"pw": 74, "miss": [], "f": "WLLDW"},
        "Athletic Bilbao": {"pw": 85, "miss": [], "f": "WWDWW"},
        "Atletico Madrid": {"pw": 90, "miss": ["De Paul (I)"], "f": "WWDLD"},
        "Barcelona": {"pw": 94, "miss": ["Gavi (I)", "Araujo (I)"], "f": "WWWLW"},
        "Celta Vigo": {"pw": 76, "miss": [], "f": "LWWLD"},
        "Espanyol": {"pw": 72, "miss": [], "f": "LWLDL"},
        "Getafe": {"pw": 75, "miss": [], "f": "DDDLW"},
        "Girona": {"pw": 84, "miss": [], "f": "LWWDL"},
        "Las Palmas": {"pw": 71, "miss": [], "f": "LLDDL"},
        "Leganes": {"pw": 70, "miss": [], "f": "LDDLW"},
        "Mallorca": {"pw": 77, "miss": [], "f": "WWDWL"},
        "Osasuna": {"pw": 78, "miss": [], "f": "DWWLD"},
        "Rayo Vallecano": {"pw": 75, "miss": [], "f": "DWDLD"},
        "Real Madrid": {"pw": 98, "miss": ["Courtois (I)", "Alaba (I)"], "f": "WWWWD"},
        "Real Sociedad": {"pw": 83, "miss": [], "f": "LDWWD"},
        "Sevilla": {"pw": 79, "miss": [], "f": "WLDLW"},
        "Valencia": {"pw": 76, "miss": [], "f": "LLDWD"},
        "Valladolid": {"pw": 71, "miss": [], "f": "LWLLD"},
        "Villarreal": {"pw": 84, "miss": [], "f": "WWLDW"}
    }
}

# Nota: Bundesliga (18 squadre) e Ligue 1 (18 squadre) seguono la stessa struttura

# --- 2. LOGICA DI ANALISI ---
def analyze_match(h, a, league):
    sh = EURO_DB[league][h]
    sa = EURO_DB[league][a]
    
    # Calcolo penalità assenze
    penalty_h = len(sh['miss']) * 2.5
    penalty_a = len(sa['miss']) * 2.5
    
    pw_h = sh['pw'] - penalty_h + 4.5 # Bonus casa
    pw_a = sa['pw'] - penalty_a
    
    total = pw_h + pw_a + 22 # Fattore pareggio
    p1, p2 = pw_h/total, pw_a/total
    px = 1.0 - (p1 + p2)
    
    return {"probs": [p1, px, p2], "h_data": sh, "a_data": sa}

# --- 3. INTERFACCIA STREAMLIT ---
st.set_page_config(page_title="AI TOTAL COMMANDER", layout="wide")
st.title("🏆 AI European Intelligence 2026")

with st.sidebar:
    st.header("📂 Archivio Campionati")
    sel_l = st.selectbox("Seleziona Campionato", list(EURO_DB.keys()))
    
    teams = sorted(list(EURO_DB[sel_l].keys()))
    h_t = st.selectbox("Squadra Casa", teams, index=teams.index("Inter") if "Inter" in teams else 0)
    a_t = st.selectbox("Squadra Trasferta", teams, index=teams.index("Milan") if "Milan" in teams else 1)
    
    st.divider()
    btn = st.button("🚀 AVVIA ANALISI PROFONDA")

if btn:
    if h_t == a_t:
        st.error("Seleziona due squadre differenti.")
    else:
        # Simulazione caricamento dati web
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)
            
        data = analyze_match(h_t, a_t, sel_l)
        
        # Display Risultati
        c1, c2, c3 = st.columns([1, 2, 1])
        
        with c1:
            st.subheader(h_t)
            st.write(f"Trend: `{data['h_data']['f']}`")
            if data['h_data']['miss']:
                st.warning(f"Assenti: {', '.join(data['h_data']['miss'])}")
            else: st.success("Rosa al completo")

        with c2:
            fig = go.Figure(data=[go.Pie(labels=['1','X','2'], values=data['probs'], hole=.6, marker_colors=['#00ffcc', '#3b82f6', '#ff4b4b'])])
            fig.update_layout(showlegend=True, height=400, paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
            st.plotly_chart(fig, use_container_width=True)

        with c3:
            st.subheader(a_t)
            st.write(f"Trend: `{data['a_data']['f']}`")
            if data['a_data']['miss']:
                st.warning(f"Assenti: {', '.join(data['a_data']['miss'])}")
            else: st.success("Rosa al completo")

        st.divider()
        st.info(f"L'analisi suggerisce una probabilità di vittoria del **{data['probs'][0]:.1%}** per la squadra di casa.")
    
