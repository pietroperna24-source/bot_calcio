import streamlit as st
import time
import random
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CONFIGURAZIONE E STILE (UI CLEAN) ---
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
    <div class="custom-label">🛰️ AI AUTOMATIC SYNC: ON</div>
""", unsafe_allow_html=True)

# --- 2. DATABASE INTEGRALE (CORE DATA) ---
EURO_DB = {
    "Serie A 🇮🇹": {
        "Inter": {"pw": 94, "miss": ["Barella (S)"], "f": "WWWDW", "style": [9,8,9,7,9], "color": "#006294"},
        "Milan": {"pw": 88, "miss": ["Maignan (I)"], "f": "WDLWW", "style": [8,7,8,8,7], "color": "#fb1107"},
        "Juventus": {"pw": 88, "miss": ["Vlahovic (I)"], "f": "WWDDW", "style": [6,9,7,9,6], "color": "#ffffff"},
        "Napoli": {"pw": 87, "miss": ["Osimhen (N)"], "f": "LWWLD", "style": [8,7,9,6,8], "color": "#0091ff"},
        "Atalanta": {"pw": 86, "miss": ["Lookman (I)"], "f": "WWWLD", "style": [9,6,8,7,9], "color": "#00539c"},
        "Roma": {"pw": 83, "miss": ["Dybala (I)"], "f": "DDWLW", "style": [7,7,8,7,7], "color": "#8e001c"},
        "Lazio": {"pw": 82, "miss": [], "f": "LWLDW", "style": [7,6,7,7,8], "color": "#87d3f8"},
        "Fiorentina": {"pw": 81, "miss": [], "f": "WWDLD", "style": [8,6,8,6,7], "color": "#4b2e83"}
    },
    "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": {
        "Man City": {"pw": 97, "miss": ["Rodri (I)"], "f": "WWWWW", "style": [10,8,10,7,9], "color": "#6caee0"},
        "Arsenal": {"pw": 95, "miss": ["Saka (I)"], "f": "WWWLW", "style": [9,9,9,8,8], "color": "#ef0107"},
        "Liverpool": {"pw": 94, "miss": ["Salah (I)"], "f": "WWDWW", "style": [10,7,10,6,10], "color": "#e31b23"},
        "Chelsea": {"pw": 85, "miss": ["James (I)"], "f": "LDWWW", "style": [8,6,8,6,8], "color": "#034694"},
        "Man United": {"pw": 83, "miss": ["Shaw (I)"], "f": "WLLDW", "style": [8,6,8,6,8], "color": "#da291c"}
    }
}

# --- 3. MOTORE DI AUTOMAZIONE (PALINSESTO DINAMICO) ---
def generate_auto_schedule(league):
    """Genera automaticamente i match in base alle squadre nel database."""
    teams = list(EURO_DB[league].keys())
    random.seed(datetime.now().strftime("%Y%m%d")) # Cambia match ogni giorno
    random.shuffle(teams)
    
    auto_matches = []
    for i in range(0, len(teams)-1, 2):
        time_slot = random.choice(["15:00", "18:00", "20:45", "21:00"])
        auto_matches.append((teams[i], teams[i+1], time_slot))
    return auto_matches

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
st.title("🛡️ AI NEURAL COMMANDER v5.0")
st.write(f"Data Corrente: **{datetime.now().strftime('%d/%m/%Y')}**")

tab_live, tab_reg = st.tabs(["🚀 PALINSESTO AUTOMATICO", "👤 REGISTRAZIONE UTENTE"])

with tab_live:
    col_list, col_res = st.columns([1, 2.5])

    with col_list:
        st.markdown('<div class="data-card">', unsafe_allow_html=True)
        st.subheader("🏆 Eventi del Giorno")
        l_sel = st.selectbox("Campionato", list(EURO_DB.keys()))
        
        # Generazione Automatica
        matches = generate_auto_schedule(l_sel)
        match_options = [f"{m[0]} vs {m[1]} ({m[2]})" for m in matches]
        
        sel_match_txt = st.radio("Seleziona Match da analizzare:", match_options)
        
        # Split dei dati selezionati
        h_sel = sel_match_txt.split(" vs ")[0]
        a_sel = sel_match_txt.split(" vs ")[1].split(" (")[0]
        st.markdown('</div>', unsafe_allow_html=True)

    with col_res:
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

            c_l, c_m, c_r = st.columns([1, 1.5, 1])

            with c_l:
                st.markdown('<div class="data-card">', unsafe_allow_html=True)
                st.markdown(f"<p class='stat-label'>Stato Rosa</p><p class='stat-value'>{hh}%</p>", unsafe_allow_html=True)
                if sh['miss']: st.markdown(f"<div class='absent-tag'>🚑 {', '.join(sh['miss'])}</div>", unsafe_allow_html=True)
                fig_r1 = go.Figure(data=go.Scatterpolar(r=sh['style'], theta=['Att','Dif','Pos','Fis','Vel'], fill='toself', line_color=sh['color']))
                fig_r1.update_layout(polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(visible=False, range=[0, 10])), showlegend=False, height=200, margin=dict(t=10,b=10,l=20,r=20), paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_r1, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with c_m:
                st.markdown('<div class="data-card" style="text-align:center;">', unsafe_allow_html=True)
                fig_p = go.Figure(go.Pie(labels=['1', 'X', '2'], values=p, hole=.7, marker_colors=[sh['color'], '#1e293b', sa['color']]))
                fig_p.update_layout(showlegend=False, height=250, margin=dict(t=0,b=0,l=0,r=0), paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_p, use_container_width=True)
                st.markdown(f"<p class='stat-label'>Fiducia AI</p><p class='stat-value'>{max(p)*100:.1f}%</p>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with c_r:
                st.markdown('<div class="data-card">', unsafe_allow_html=True)
                st.markdown(f"<p class='stat-label'>Stato Rosa</p><p class='stat-value'>{ha}%</p>", unsafe_allow_html=True)
                if sa['miss']: st.markdown(f"<div class='absent-tag'>🚑 {', '.join(sa['miss'])}</div>", unsafe_allow_html=True)
                fig_r2 = go.Figure(data=go.Scatterpolar(r=sa['style'], theta=['Att','Dif','Pos','Fis','Vel'], fill='toself', line_color=sa['color']))
                fig_r2.update_layout(polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(visible=False, range=[0, 10])), showlegend=False, height=200, margin=dict(t=10,b=10,l=20,r=20), paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_r2, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

with tab_reg:
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    st.subheader("👤 Registrazione Utente")
    with st.form("reg"):
        st.text_input("Username")
        st.text_input("Email")
        if st.form_submit_button("ATTIVA NOTIFICHE PRO"):
            st.success("Sincronizzazione attivata con il server 2026.")
    st.markdown('</div>', unsafe_allow_html=True)
