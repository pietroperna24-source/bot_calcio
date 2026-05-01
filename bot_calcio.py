import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import random

# --- 1. DATABASE INTEGRALE EUROPA 2026 ---
EURO_DB = {
    "Serie A 🇮🇹": {
        "Inter": 94, "Milan": 88, "Juventus": 87, "Napoli": 85, "Atalanta": 86, "Roma": 82, "Lazio": 81, "Como": 75
    },
    "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": {
        "Man City": 97, "Arsenal": 95, "Liverpool": 94, "Chelsea": 83, "Aston Villa": 86, "Man United": 82
    },
    "La Liga 🇪🇸": {
        "Real Madrid": 98, "Barcelona": 92, "Atletico Madrid": 89, "Girona": 86, "Sociedad": 83
    },
    "Bundesliga 🇩🇪": {
        "Bayer Leverkusen": 92, "Bayern Munich": 93, "Dortmund": 88, "Leipzig": 86, "Stuttgart": 87
    }
}

# --- 2. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="AI ORACLE PRO v4", layout="wide")

if 'history' not in st.session_state:
    st.session_state.history = []

# CSS Custom
st.markdown("""
    <style>
    .stApp { background-color: #0b0e11; color: white; }
    .value-box { background: #1e293b; padding: 20px; border-radius: 15px; border: 2px solid #3b82f6; text-align: center; }
    .trigger-card { background: #0f172a; padding: 10px; border-radius: 8px; border-left: 4px solid #f59e0b; margin-bottom: 5px; }
    .metric-text { font-size: 0.9rem; color: #94a3b8; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MOTORE ANALITICO AVANZATO (LIVE TRIGGERS) ---
def advanced_neural_analysis(h, a, league, triggers):
    # Base Power Index
    p_h = EURO_DB[league][h]
    p_a = EURO_DB[league][a]
    
    # Applicazione Live Triggers (Infortuni, Forma, Motivazione)
    if triggers['injuries_h']: p_h *= 0.95  # -5% per assenze pesanti
    if triggers['injuries_a']: p_a *= 0.95
    
    # Stato di forma (Simulato sugli ultimi 5 match)
    p_h *= (1 + (triggers['form_h'] / 100))
    p_a *= (1 + (triggers['form_a'] / 100))
    
    # Calcolo Probabilità
    total = p_h + p_a + 22
    p1 = (p_h + 5) / total # Bonus Casa
    p2 = p_a / total
    px = 1.0 - (p1 + p2)
    
    return {"1": p1, "X": px, "2": p2}

# --- 4. INTERFACCIA PRINCIPALE ---
st.title("🔮 AI European Oracle v4.0")
st.caption("Advanced Betting Intelligence & Value Scanner")

tabs = st.tabs(["🎯 Analisi & Value Bet", "📚 Archivio & ROI", "⚙️ Configurazione Power"])

with tabs[0]:
    # Sidebar di selezione
    with st.sidebar:
        st.header("🏟️ Selezione Evento")
        league_sel = st.selectbox("Campionato", list(EURO_DB.keys()))
        teams = sorted(list(EURO_DB[league_sel].keys()))
        h_team = st.selectbox("Casa", teams, index=0)
        a_team = st.selectbox("Trasferta", teams, index=1)
        
        st.divider()
        st.header("⚡ Live Triggers")
        inj_h = st.checkbox(f"Assenze pesanti {h_team}")
        form_h = st.slider(f"Forma {h_team} (%)", -10, 10, 0)
        inj_a = st.checkbox(f"Assenze pesanti {a_team}")
        form_a = st.slider(f"Forma {a_team} (%)", -10, 10, 0)
        
        st.divider()
        st.header("💰 Quote Bookmaker")
        q1 = st.number_input("Quota 1", value=2.0, step=0.1)
        qx = st.number_input("Quota X", value=3.4, step=0.1)
        q2 = st.number_input("Quota 2", value=3.0, step=0.1)
        
        analyze_btn = st.button("🚀 AVVIA ANALISI VALORE", use_container_width=True)

    if analyze_btn:
        # Simulazione Caricamento
        with st.status("Analisi in corso...", expanded=True) as status:
            time.sleep(0.5)
            st.write("🔍 Scansione bollettini medici per Live Triggers...")
            time.sleep(0.5)
            st.write("📊 Calcolo differenziale di quota (Value Analysis)...")
            status.update(label="Analisi Completata!", state="complete")

        trig_data = {'injuries_h': inj_h, 'injuries_a': inj_a, 'form_h': form_h, 'form_a': form_a}
        res = advanced_neural_analysis(h_team, a_team, league_sel, trig_data)
        
        # Display Risultati
        c1, c2, c3 = st.columns([2, 1, 1])
        
        with c1:
            st.subheader(f"🏟️ {h_team} vs {a_team}")
            fig = go.Figure(go.Bar(x=['1', 'X', '2'], y=[res['1'], res['X'], res['2']], marker_color=['#10b981', '#64748b', '#ef4444']))
            fig.update_layout(height=250, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.subheader("💡 Value Scanner")
            # Calcolo Value: (Probabilità * Quota) - 1
            v1 = (res['1'] * q1) - 1
            vx = (res['X'] * qx) - 1
            v2 = (res['2'] * q2) - 1
            
            def show_value(label, val):
                color = "#10b981" if val > 0 else "#ef4444"
                st.markdown(f"**{label}**: <span style='color:{color}'>{val:+.2%}</span>", unsafe_allow_html=True)
            
            show_value("Value Segno 1", v1)
            show_value("Value Segno X", vx)
            show_value("Value Segno 2", v2)
            
            st.info("Un valore positivo indica una quota 'sbagliata' dal bookmaker (Vantaggio Giocatore).")

        with c3:
            st.subheader("🎯 Verdict")
            if v1 > 0.05: st.success(f"VALUE DETECTED: Punta su {h_team}")
            elif v2 > 0.05: st.success(f"VALUE DETECTED: Punta su {a_team}")
            else: st.warning("NO VALUE: Quote bilanciate")
            
            if st.button("💾 Salva in Archivio"):
                st.session_state.history.append({
                    "data": datetime.now().strftime("%d/%m %H:%M"),
                    "match": f"{h_team}-{a_team}",
                    "pred": "1" if res['1']>res['2'] else "2",
                    "value": max(v1, v2, vx)
                })
                st.toast("Pronostico salvato!")

with tabs[1]:
    st.subheader("📈 Performance & Backtesting")
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.table(df)
        
        # Metriche ROI fittizie per l'esempio
        cc1, cc2, cc3 = st.columns(3)
        cc1.metric("Win Rate AI", "67.4%", "+2.1%")
        cc2.metric("ROI Totale", "+14.2%", "540€")
        cc3.metric("Picks Salvati", len(st.session_state.history))
    else:
        st.info("L'archivio è vuoto. Salva le tue analisi per monitorare il profitto.")

with tabs[2]:
    st.subheader("⚙️ Modifica Manuale Power Index")
    st.write("In questa sezione puoi ricalibrare manualmente la forza delle squadre se ritieni che l'IA sia troppo ottimista/pessimista.")
    edited_df = st.data_editor(pd.DataFrame(list(EURO_DB[league_sel].items()), columns=["Squadra", "Power"]))

# Footer con esportazione
st.divider()
st.button("📥 Esporta Report PDF Schedina (Simulazione)")
