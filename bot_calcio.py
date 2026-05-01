import streamlit as st
import time
import random
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CONFIGURAZIONE INTERFACCIA ---
st.set_page_config(page_title="AI NEURAL COMMANDER 2026", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    header[data-testid="stHeader"] { visibility: hidden; height: 0px; }
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    .stApp { background-color: #05070a; color: #e0e0e0; }
    
    .data-card {
        background: rgba(30, 41, 59, 0.25);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
    }
    
    .vs-badge {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white; padding: 5px 20px; border-radius: 30px;
        font-weight: 900; font-size: 1.5rem; display: inline-block;
    }

    .stat-label { color: #94a3b8; font-size: 0.85rem; text-transform: uppercase; }
    .stat-value { font-size: 1.8rem; font-weight: 700; color: #3b82f6; }
    
    .custom-label {
        position: fixed; top: 10px; right: 20px; z-index: 1000;
        color: #3b82f6; background: rgba(15, 23, 42, 0.9);
        padding: 5px 15px; border: 1px solid #3b82f6; border-radius: 8px;
        font-weight: bold; font-size: 11px;
    }
    </style>
    <div class="custom-label">🛰️ FULL DATABASE SYNC: 2026 ACTIVE</div>
""", unsafe_allow_html=True)

# --- 2. DATABASE INTEGRALE (Tutte le squadre dei campionati 2026) ---
EURO_DB = {
    "Serie A 🇮🇹": {
        "Atalanta": {"pw": 86, "miss": [], "f": "WWWLD", "style": [9,6,8,7,9], "color": "#00539c"},
        "Bologna": {"pw": 79, "miss": [], "f": "DDWLW", "style": [7,7,8,6,7], "color": "#a7171a"},
        "Cagliari": {"pw": 71, "miss": [], "f": "LLDDW", "style": [5,8,5,8,6], "color": "#002350"},
        "Como": {"pw": 76, "miss": [], "f": "WLDLW", "style": [7,6,8,6,7], "color": "#003399"},
        "Empoli": {"pw": 70, "miss": [], "f": "LDDWL", "style": [5,8,6,7,5], "color": "#005baa"},
        "Fiorentina": {"pw": 81, "miss": [], "f": "WWDLD", "style": [8,6,8,6,7], "color": "#4b2e83"},
        "Genoa": {"pw": 76, "miss": [], "f": "DWLLW", "style": [6,7,6,8,7], "color": "#a7171a"},
        "Inter": {"pw": 94, "miss": ["Barella (S)"], "f": "WWWDW", "style": [9,8,9,7,9], "color": "#006294"},
        "Juventus": {"pw": 88, "miss": ["Vlahovic (I)"], "f": "WWDDW", "style": [6,9,7,9,6], "color": "#ffffff"},
        "Lazio": {"pw": 82, "miss": [], "f": "LWLDW", "style": [7,6,7,7,8], "color": "#87d3f8"},
        "Lecce": {"pw": 72, "miss": [], "f": "LLDWL", "style": [6,7,5,8,7], "color": "#ffed00"},
        "Milan": {"pw": 88, "miss": ["Maignan (I)"], "f": "WDLWW", "style": [8,7,8,8,7], "color": "#fb1107"},
        "Monza": {"pw": 74, "miss": [], "f": "LDDWW", "style": [6,7,7,6,6], "color": "#e30613"},
        "Napoli": {"pw": 87, "miss": ["Osimhen (N)"], "f": "LWWLD", "style": [8,7,9,6,8], "color": "#0091ff"},
        "Parma": {"pw": 74, "miss": [], "f": "WLDDL", "style": [7,6,6,7,8], "color": "#fff200"},
        "Roma": {"pw": 83, "miss": ["Dybala (I)"], "f": "DDWLW", "style": [7,7,8,7,7], "color": "#8e001c"},
        "Torino": {"pw": 77, "miss": [], "f": "LLWDW", "style": [6,8,6,9,7], "color": "#8a1e19"},
        "Udinese": {"pw": 74, "miss": [], "f": "WLDDW", "style": [6,8,6,8,7], "color": "#ffffff"},
        "Venezia": {"pw": 69, "miss": [], "f": "LLLWD", "style": [6,6,7,6,7], "color": "#00633c"},
        "Verona": {"pw": 71, "miss": [], "f": "WLLDL", "style": [5,7,6,8,7], "color": "#00357d"}
    },
    "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": {
        "Arsenal": {"pw": 95, "miss": ["Saka (I)"], "f": "WWWLW", "style": [9,9,9,8,8], "color": "#ef0107"},
        "Aston Villa": {"pw": 86, "miss": [], "f": "WWDWL", "style": [8,7,8,8,8], "color": "#95bfe5"},
        "Bournemouth": {"pw": 76, "miss": [], "f": "WLDDW", "style": [7,6,6,7,8], "color": "#da291c"},
        "Brentford": {"pw": 77, "miss": [], "f": "LWDWW", "style": [7,6,6,8,8], "color": "#e30613"},
        "Brighton": {"pw": 82, "miss": [], "f": "DWWLD", "style": [8,6,9,6,8], "color": "#0057b8"},
        "Chelsea": {"pw": 85, "miss": ["James (I)"], "f": "LDWWW", "style": [8,6,8,6,8], "color": "#034694"},
        "Crystal Palace": {"pw": 75, "miss": [], "f": "DDLWW", "style": [6,8,6,8,7], "color": "#1b458f"},
        "Everton": {"pw": 73, "miss": [], "f": "LLLDW", "style": [5,9,5,9,6], "color": "#003399"},
        "Fulham": {"pw": 76, "miss": [], "f": "WDDLW", "style": [7,7,7,7,7], "color": "#ffffff"},
        "Ipswich": {"pw": 68, "miss": [], "f": "LLLDD", "style": [6,6,6,7,7], "color": "#3a5dae"},
        "Leicester": {"pw": 71, "miss": [], "f": "LDDLW", "style": [6,7,6,7,7], "color": "#003090"},
        "Liverpool": {"pw": 94, "miss": ["Salah (I)"], "f": "WWDWW", "style": [10,7,10,6,10], "color": "#e31b23"},
        "Man City": {"pw": 97, "miss": ["Rodri (I)"], "f": "WWWWW", "style": [10,8,10,7,9], "color": "#6caee0"},
        "Man United": {"pw": 83, "miss": ["Shaw (I)"], "f": "WLLDW", "style": [8,6,8,6,8], "color": "#da291c"},
        "Newcastle": {"pw": 84, "miss": [], "f": "WLDWW", "style": [8,7,7,8,9], "color": "#ffffff"},
        "Nottm Forest": {"pw": 74, "miss": [], "f": "DWWLD", "style": [6,8,6,8,7], "color": "#e53233"},
        "Southampton": {"pw": 69, "miss": [], "f": "LLLLL", "style": [6,6,7,6,6], "color": "#d71920"},
        "Tottenham": {"pw": 86, "miss": ["Son (I)"], "f": "DWLWW", "style": [9,6,8,6,10], "color": "#132257"},
        "West Ham": {"pw": 78, "miss": [], "f": "LDDLW", "style": [7,7,7,8,7], "color": "#7a263a"},
        "Wolves": {"pw": 72, "miss": [], "f": "LLLDL", "style": [6,7,6,8,8], "color": "#fdb913"}
    }
}

# --- 3. LOGICA DI AUTOMAZIONE COMPLETA ---
def get_daily_schedule(league):
    """Genera un palinsesto completo di tutti i club per la giornata corrente."""
    teams = sorted(list(EURO_DB[league].keys()))
    # Seed basato sulla data odierna per rendere il calendario fisso per 24h
    random.seed(datetime.now().strftime("%Y%m%d"))
    random.shuffle(teams)
    
    daily_matches = []
    times = ["12:30", "15:00", "18:00", "18:30", "20:45", "21:00"]
    
    for i in range(0, len(teams), 2):
        if i+1 < len(teams):
            match_time = random.choice(times)
            daily_matches.append((teams[i], teams[i+1], match_time))
    return daily_matches

def get_analysis(h, a, league):
    sh, sa = EURO_DB[league][h], EURO_DB[league][a]
    hh = max(10, 100 - (len(sh['miss']) * 15))
    ha = max(10, 100 - (len(sa['miss']) * 15))
    pw_h = (sh['pw'] * (hh/100)) + 5 
    pw_a = (sa['pw'] * (ha/100))
    total = pw_h + pw_a + 25
    probs = [pw_h/total, 25/total, pw_a/total]
    return probs, hh, ha

# --- 4. INTERFACCIA PRINCIPALE ---
st.title("🛡️ AI NEURAL COMMANDER v6.0")
st.write(f"Sincronizzazione Palinsesto: **{datetime.now().strftime('%d/%B/%Y')}**")

tab_cmd, tab_user = st.tabs(["🚀 ANALISI EVENTI REAL-TIME", "👤 REGISTRAZIONE PRO"])

with tab_cmd:
    col_menu, col_report = st.columns([1, 2.3])

    with col_menu:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.subheader("📅 Palinsesto Automatico")
        l_sel = st.selectbox("Campionato", list(EURO_DB.keys()))
        
        matches = get_daily_schedule(l_sel)
        match_labels = [f"{m[0]} vs {m[1]} (h {m[2]})" for m in matches]
        
        sel_match_label = st.radio("Seleziona scontro:", match_labels)
        
        # Estrazione nomi squadre
        h_sel = sel_match_label.split(" vs ")[0]
        a_sel = sel_match_label.split(" vs ")[1].split(" (")[0]
        st.markdown('</div>', unsafe_allow_html=True)

    with col_report:
        if h_sel and a_sel:
            p, hh, ha = get_analysis(h_sel, a_sel, l_sel)
            sh, sa = EURO_DB[l_sel][h_sel], EURO_DB[l_sel][a_sel]

            st.markdown(f"""
                <div style='text-align: center; margin-bottom: 30px;'>
                    <h1 style='display: inline; color:{sh['color']};'>{h_sel.upper()}</h1>
                    <span class='vs-badge'>VS</span>
                    <h1 style='display: inline; color:{sa['color']};'>{a_sel.upper()}</h1>
                </div>
            """, unsafe_allow_html=True)

            c_l, c_m, c_r = st.columns([1, 1.4, 1])

            with c_l:
                st.markdown('<div class="data-card">', unsafe_allow_html=True)
                st.markdown(f"<p class='stat-label'>Integrità Rosa</p><p class='stat-value'>{hh}%</p>", unsafe_allow_html=True)
                if sh['miss']: st.markdown(f"<div style='color:#ef4444; font-size:0.8rem;'>🚑 {', '.join(sh['miss'])}</div>", unsafe_allow_html=True)
                fig_r1 = go.Figure(data=go.Scatterpolar(r=sh['style'], theta=['Att','Dif','Pos','Fis','Vel'], fill='toself', line_color=sh['color']))
                fig_r1.update_layout(polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(visible=False, range=[0, 10])), showlegend=False, height=200, margin=dict(t=10,b=10,l=20,r=20), paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_r1, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with c_m:
                st.markdown('<div class="data-card" style="text-align:center;">', unsafe_allow_html=True)
                fig_pie = go.Figure(go.Pie(labels=['1', 'X', '2'], values=p, hole=.7, marker_colors=[sh['color'], '#1e293b', sa['color']]))
                fig_pie.update_layout(showlegend=False, height=250, margin=dict(t=0,b=0,l=0,r=0), paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_pie, use_container_width=True)
                st.markdown(f"<p class='stat-label'>Fiducia AI</p><p class='stat-value'>{max(p)*100:.1f}%</p>", unsafe_allow_html=True)
                st.info(f"💡 Value Quote: > {(1/max(p)):.2f}")
                st.markdown('</div>', unsafe_allow_html=True)

            with c_r:
                st.markdown('<div class="data-card">', unsafe_allow_html=True)
                st.markdown(f"<p class='stat-label'>Integrità Rosa</p><p class='stat-value'>{ha}%</p>", unsafe_allow_html=True)
                if sa['miss']: st.markdown(f"<div style='color:#ef4444; font-size:0.8rem;'>🚑 {', '.join(sa['miss'])}</div>", unsafe_allow_html=True)
                fig_r2 = go.Figure(data=go.Scatterpolar(r=sa['style'], theta=['Att','Dif','Pos','Fis','Vel'], fill='toself', line_color=sa['color']))
                fig_r2.update_layout(polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(visible=False, range=[0, 10])), showlegend=False, height=200, margin=dict(t=10,b=10,l=20,r=20), paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_r2, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

with tab_user:
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    st.subheader("👤 Registrazione Utente")
    with st.form("reg"):
        st.text_input("Username")
        st.text_input("Email")
        if st.form_submit_button("ATTIVA NOTIFICHE PRO"):
            st.success("Sincronizzazione attivata con il server 2026.")
    st.markdown('</div>', unsafe_allow_html=True)
