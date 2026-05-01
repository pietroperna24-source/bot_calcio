import streamlit as st
import time
import random
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CONFIGURAZIONE E STILE (NASCONDE HEADER/FOOTER) ---
st.set_page_config(page_title="AI NEURAL COMMANDER PRO", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    /* Nasconde header, menu e footer di sistema */
    header[data-testid="stHeader"] { visibility: hidden; height: 0px; }
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    
    .stApp { background-color: #05070a; color: #e0e0e0; }
    
    /* Card moderne con effetto vetro */
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
        color: white;
        padding: 5px 20px;
        border-radius: 30px;
        font-weight: 900;
        font-size: 1.5rem;
        display: inline-block;
        margin: 10px 0;
    }

    .stat-label { color: #94a3b8; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 1px; }
    .stat-value { font-size: 1.8rem; font-weight: 700; color: #3b82f6; }
    
    .absent-tag {
        background: rgba(239, 68, 68, 0.15);
        border-left: 4px solid #ef4444;
        padding: 8px 12px;
        border-radius: 5px;
        margin-top: 10px;
        font-size: 0.9rem;
    }

    .custom-label {
        position: fixed; top: 10px; right: 20px; z-index: 1000;
        color: #3b82f6; background: rgba(15, 23, 42, 0.9);
        padding: 5px 15px; border: 1px solid #3b82f6; border-radius: 8px;
        font-weight: bold; font-size: 11px; letter-spacing: 1px;
    }
    </style>
    <div class="custom-label">🛰️ NEURAL SERVER 2026 ONLINE</div>
""", unsafe_allow_html=True)

# --- 2. DATABASE INTEGRALE EUROPA 2026 (98 SQUADRE) ---
EURO_DB = {
    "Serie A 🇮🇹": {
        "Atalanta": {"pw": 86, "miss": ["Scamacca (I)"], "f": "WWWLD", "style": [9,6,8,7,9], "color": "#00539c"},
        "Bologna": {"pw": 79, "miss": [], "f": "DDWLW", "style": [7,7,8,6,7], "color": "#a7171a"},
        "Cagliari": {"pw": 71, "miss": [], "f": "LLDDW", "style": [5,8,5,8,6], "color": "#002350"},
        "Como": {"pw": 76, "miss": ["Varane (I)"], "f": "WLDLW", "style": [7,6,8,6,7], "color": "#003399"},
        "Empoli": {"pw": 70, "miss": [], "f": "LDDWL", "style": [5,8,6,7,5], "color": "#005baa"},
        "Fiorentina": {"pw": 81, "miss": [], "f": "WWDLD", "style": [8,6,8,6,7], "color": "#4b2e83"},
        "Genoa": {"pw": 76, "miss": [], "f": "DWLLW", "style": [6,7,6,8,7], "color": "#a7171a"},
        "Inter": {"pw": 94, "miss": ["Barella (S)", "Bastoni (I)"], "f": "WWWDW", "style": [9,8,9,7,9], "color": "#006294"},
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
        "Barcelona": {"pw": 94, "miss": ["Gavi (I)"], "f": "WWWLW", "style": [9,6,10,6,8], "color": "#a50044"},
        "Real Madrid": {"pw": 98, "miss": ["Courtois (I)"], "f": "WWWWD", "style": [10,8,9,8,10], "color": "#ffffff"},
        "Atletico Madrid": {"pw": 90, "miss": ["De Paul (I)"], "f": "WWDLD", "style": [7,10,7,10,7], "color": "#cb3524"},
        "Villarreal": {"pw": 84, "miss": [], "f": "WWLDW", "style": [8,6,8,6,8], "color": "#ffe600"}
    }
}

# --- 3. ENGINE ANALITICO ---
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

tab_cmd, tab_user = st.tabs(["🎮 CENTRALE ANALISI", "👤 REGISTRAZIONE & NEWSLETTER"])

with tab_cmd:
    # Selezione Evento
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    st.subheader("📂 Catalogo Eventi")
    c_l, c_h, c_a = st.columns(3)
    with c_l:
        l_sel = st.selectbox("Campionato", list(EURO_DB.keys()))
    t_list = sorted(list(EURO_DB[l_sel].keys()))
    with c_h:
        h_sel = st.selectbox("Team Casa", t_list, index=0)
    with c_a:
        a_sel = st.selectbox("Team Trasferta", t_list, index=1 if len(t_list)>1 else 0)
    
    btn = st.button("🚀 AVVIA REPORT DI INTELLIGENCE", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if btn:
        if h_sel == a_sel:
            st.error("Seleziona squadre diverse.")
        else:
            with st.status("🧠 Elaborazione dati neurale...", expanded=True) as status:
                time.sleep(0.5); st.write("📥 Caricamento database..."); time.sleep(0.5)
                status.update(label="Analisi Completata!", state="complete")
            
            p, hh, ha = get_analysis(h_sel, a_sel, l_sel)
            sh, sa = EURO_DB[l_sel][h_sel], EURO_DB[l_sel][a_sel]

            # Header Grafico
            st.markdown(f"""
                <div style='text-align: center; margin-bottom: 30px;'>
                    <h1 style='display: inline; color:{sh['color']};'>{h_sel.upper()}</h1>
                    <span class='vs-badge'>VS</span>
                    <h1 style='display: inline; color:{sa['color']};'>{a_sel.upper()}</h1>
                </div>
            """, unsafe_allow_html=True)

            col_left, col_mid, col_right = st.columns([1.2, 2, 1.2])

            with col_left:
                st.markdown(f'<div class="data-card">', unsafe_allow_html=True)
                st.markdown(f"<p class='stat-label'>Stato Rosa</p><p class='stat-value'>{hh}%</p>", unsafe_allow_html=True)
                st.write(f"**Trend:** `{sh['f']}`")
                if sh['miss']:
                    st.markdown(f"<div class='absent-tag'>🚑 {', '.join(sh['miss'])}</div>", unsafe_allow_html=True)
                
                fig_r1 = go.Figure(data=go.Scatterpolar(r=sh['style'], theta=['Att','Dif','Pos','Fis','Vel'], fill='toself', line_color=sh['color']))
                fig_r1.update_layout(polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(visible=False, range=[0, 10])), showlegend=False, height=220, margin=dict(t=10,b=10,l=30,r=30), paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_r1, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_mid:
                st.markdown(f'<div class="data-card" style="text-align:center;">', unsafe_allow_html=True)
                st.markdown("<p class='stat-label'>Probabilità Esito</p>", unsafe_allow_html=True)
                fig_p = go.Figure(go.Pie(labels=['1', 'X', '2'], values=p, hole=.7, marker_colors=[sh['color'], '#1e293b', sa['color']]))
                fig_p.update_layout(showlegend=False, height=300, margin=dict(t=0,b=0,l=0,r=0), paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_p, use_container_width=True)
                
                conf = max(p) * 100
                st.markdown(f"<p class='stat-label'>Fiducia AI</p><p class='stat-value' style='font-size:3rem;'>{conf:.1f}%</p>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                fair_odd = 1/max(p)
                st.info(f"💡 Suggerimento IA: Quota minima consigliata sopra {fair_odd:.2f}")

            with col_right:
                st.markdown(f'<div class="data-card">', unsafe_allow_html=True)
                st.markdown(f"<p class='stat-label'>Stato Rosa</p><p class='stat-value'>{ha}%</p>", unsafe_allow_html=True)
                st.write(f"**Trend:** `{sa['f']}`")
                if sa['miss']:
                    st.markdown(f"<div class='absent-tag'>🚑 {', '.join(sa['miss'])}</div>", unsafe_allow_html=True)
                
                fig_r2 = go.Figure(data=go.Scatterpolar(r=sa['style'], theta=['Att','Dif','Pos','Fis','Vel'], fill='toself', line_color=sa['color']))
                fig_r2.update_layout(polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(visible=False, range=[0, 10])), showlegend=False, height=220, margin=dict(t=10,b=10,l=30,r=30), paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_r2, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

with tab_user:
    st.markdown('<div class="data-card">', unsafe_allow_html=True)
    st.subheader("👤 Registrazione Utente")
    st.write("Iscriviti per ricevere aggiornamenti sulle formazioni e i segnali Value Bet dell'IA.")
    with st.form("reg_pro"):
        u_name = st.text_input("Username")
        u_email = st.text_input("Email")
        u_pref = st.multiselect("Campionati preferiti", list(EURO_DB.keys()))
        u_sub = st.form_submit_button("ATTIVA NOTIFICHE PRO")
        if u_sub:
            if u_name and u_email:
                st.success(f"Benvenuto {u_name}! Il tuo account è ora collegato al server neurale.")
            else:
                st.error("Dati incompleti.")
    st.markdown('</div>', unsafe_allow_html=True)
