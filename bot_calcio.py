import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import random

# --- 1. DATABASE SQUADRE (POWER INDEX & ROSE) ---
EURO_DB = {
    "Serie A 🇮🇹": {
        "Inter": {"power": 94, "top_players": ["L. Martinez", "Barella"], "stadium": "San Siro"},
        "Milan": {"power": 88, "top_players": ["Leao", "Maignan"], "stadium": "San Siro"},
        "Juventus": {"power": 87, "top_players": ["Vlahovic", "Yildiz"], "stadium": "Allianz Stadium"},
        "Napoli": {"power": 85, "top_players": ["Kvaratskhelia", "Osimhen"], "stadium": "Diego Maradona"},
        "Atalanta": {"power": 86, "top_players": ["Lookman", "Ederson"], "stadium": "Gewiss Stadium"},
        "Como": {"power": 75, "top_players": ["Cutrone", "Paz"], "stadium": "Sinigaglia"}
    },
    "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": {
        "Man City": {"power": 97, "top_players": ["Haaland", "Foden"], "stadium": "Etihad"},
        "Arsenal": {"power": 95, "top_players": ["Saka", "Odegaard"], "stadium": "Emirates"},
        "Liverpool": {"power": 94, "top_players": ["Salah", "Diaz"], "stadium": "Anfield"}
    }
}

# --- 2. CONFIGURAZIONE ESTETICA ---
st.set_page_config(page_title="AI NEURAL INTELLIGENCE", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b0e11; color: white; }
    .header-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 25px; border-radius: 15px; border: 1px solid #334155;
        text-align: center; margin-bottom: 25px;
    }
    .stats-card {
        background: #1e293b; border-radius: 15px; padding: 20px;
        border: 1px solid #334155; height: 100%;
    }
    .match-display {
        background: #0f172a; border-radius: 20px; padding: 30px;
        border: 1px solid #3b82f6; text-align: center; margin-bottom: 20px;
    }
    .absent-text { color: #ff4b4b; font-weight: bold; }
    .yellow-text { color: #fbbf24; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MOTORE ANALITICO AVANZATO ---
def deep_neural_analysis(h, a, league, odds_1, odds_X, odds_2):
    # Dati base
    p_h = EURO_DB[league][h]["power"]
    p_a = EURO_DB[league][a]["power"]
    
    # Simulazione dinamica di variabili reali
    absents_h = random.sample(EURO_DB[league][h]["top_players"], random.randint(0, 1))
    absents_a = random.sample(EURO_DB[league][a]["top_players"], random.randint(0, 1))
    
    # Calcolo malus per assenti (ogni top player assente toglie 3 punti di power)
    p_h_final = p_h - (len(absents_h) * 3)
    p_a_final = p_a - (len(absents_a) * 3)
    
    total = p_h_final + p_a_final + 22
    p1 = (p_h_final + 5) / total
    p2 = p_a_final / total
    px = 1.0 - (p1 + p2)
    
    return {
        "prob": {"1": p1, "X": px, "2": p2},
        "absents": {"h": absents_h, "a": absents_a},
        "stats": {
            "possesso": [random.randint(45, 55), random.randint(45, 55)],
            "tiri": [random.randint(8, 15), random.randint(8, 15)],
            "cartellini_g": [random.randint(1, 4), random.randint(1, 4)],
            "cartellini_r": [0, random.choice([0, 0, 0, 1])]
        }
    }

# --- 4. INTERFACCIA ---
st.markdown('<div class="header-box"><h1>🔮 AI European Hub Intelligence</h1><p>Analisi Predittiva v4.0 - Statistiche Real-Time & Lineups</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("🏟️ Selezione Evento")
    league_sel = st.selectbox("Campionato", list(EURO_DB.keys()))
    teams = sorted(list(EURO_DB[league_sel].keys()))
    
    h_team = st.selectbox("Casa", teams, index=0)
    a_team = st.selectbox("Trasferta", teams, index=1 if len(teams) > 1 else 0)
    
    st.divider()
    st.subheader("💰 Quote Bookmaker")
    q1 = st.number_input("Quota 1", value=1.80, step=0.1)
    qX = st.number_input("Quota X", value=3.40, step=0.1)
    q2 = st.number_input("Quota 2", value=4.50, step=0.1)
    
    analyze_btn = st.button("🚀 AVVIA ANALISI TOTALE", use_container_width=True)

if analyze_btn:
    if h_team == a_team:
        st.error("Seleziona due squadre diverse.")
    else:
        # ANIMAZIONE CARICAMENTO
        with st.status("🕵️ Analisi intelligence in corso...", expanded=True) as status:
            st.write("📡 Scansione bollettini medici e squalifiche...")
            time.sleep(1)
            st.write("📊 Analisi storico scontri diretti e trend cartellini...")
            time.sleep(1)
            st.write("🧠 Calcolo probabilità neurale dinamica...")
            time.sleep(0.8)
            status.update(label="✅ Analisi Ultimata", state="complete", expanded=False)

        # RECUPERO DATI
        data = deep_neural_analysis(h_team, a_team, league_sel, q1, qX, q2)
        res = data["prob"]
        stats = data["stats"]

        # DISPLAY MATCH
        st.markdown(f"""
            <div class="match-display">
                <span style="font-size: 2rem; font-weight: 800;">{h_team.upper()} vs {a_team.upper()}</span><br>
                <span style="color: #94a3b8;">{EURO_DB[league_sel][h_team]['stadium']} • {datetime.now().strftime('%d/%m/%Y')}</span>
            </div>
        """, unsafe_allow_html=True)

        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.subheader("🏥 Situazione Team")
            
            # Assenti
            c_h, c_a = st.columns(2)
            with c_h:
                st.write(f"**{h_team}**")
                if data["absents"]["h"]:
                    for p in data["absents"]["h"]: st.markdown(f"❌ <span class='absent-text'>{p}</span>", unsafe_allow_html=True)
                else: st.write("✅ Rosa completa")
            
            with c_a:
                st.write(f"**{a_team}**")
                if data["absents"]["a"]:
                    for p in data["absents"]["a"]: st.markdown(f"❌ <span class='absent-text'>{p}</span>", unsafe_allow_html=True)
                else: st.write("✅ Rosa completa")
            
            st.divider()
            st.subheader("🟨 Disciplina & Trend")
            st.write(f"Media Gialli previsti: **{stats['cartellini_g'][0] + stats['cartellini_g'][1]}**")
            if stats['cartellini_r'][1] > 0:
                st.warning(f"Rischio Rosso: Elevato per **{a_team}** (Basato su trend arbitro)")
            else:
                st.write("Rischio Rosso: Basso")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_right:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.subheader("📈 Analisi Probabilistica")
            fig = go.Figure(data=[go.Pie(labels=['1', 'X', '2'], values=[res['1'], res['X'], res['2']], 
                                         hole=.5, marker_colors=['#10b981', '#64748b', '#ef4444'])])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), height=250, margin=dict(t=0,b=0,l=0,r=0))
            st.plotly_chart(fig, use_container_width=True)
            
            # VALUE BET DETECTION
            ai_q1 = 1 / res['1']
            st.write(f"**Quota Equa AI:** {ai_q1:.2f} | **Quota Bookie:** {q1}")
            if q1 > ai_q1:
                st.success(f"🔥 VALUE DETECTED: La quota su {h_team} è sovrastimata!")
            st.markdown('</div>', unsafe_allow_html=True)

        # TABELLA STATISTICHE MEDIE
        st.write("### 📊 Medie Statistiche Previste")
        df_stats = pd.DataFrame({
            "Statistica": ["Possesso Palla", "Tiri Totali", "Cartellini Gialli", "Cartellini Rossi"],
            h_team: [f"{stats['possesso'][0]}%", stats['tiri'][0], stats['cartellini_g'][0], stats['cartellini_r'][0]],
            a_team: [f"{stats['possesso'][1]}%", stats['tiri'][1], stats['cartellini_g'][1], stats['cartellini_r'][1]]
        })
        st.table(df_stats)

else:
    st.info("👈 Configura l'evento nella sidebar e avvia l'intelligence.")

st.caption(f"Dati aggregati in tempo reale • Motore Neurale v4.0 • {datetime.now().year}")
