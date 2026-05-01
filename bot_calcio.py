import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. DATABASE AVANZATO (Power Index + Stile di Gioco) ---
EURO_DB = {
    "Italia - Serie A": {
        "Inter": {"p": 92, "style": "Attacco/Contropiede"},
        "Milan": {"p": 86, "style": "Possesso"},
        "Juventus": {"p": 85, "style": "Difensivo"},
        "Napoli": {"p": 83, "style": "Attacco Posizionale"},
        "Atalanta": {"p": 84, "style": "Pressing Alto"}
    },
    "Inghilterra - Premier League": {
        "Man City": {"p": 96, "style": "Possesso Totale"},
        "Arsenal": {"p": 94, "style": "Equilibrato"},
        "Liverpool": {"p": 93, "style": "Heavy Metal Football"},
        "Man United": {"p": 82, "style": "Transizioni"}
    }
}

# --- 2. MOTORE AI DI SECONDA GENERAZIONE ---
class NeuralAnalyst:
    @staticmethod
    def deep_match_analysis(h_name, a_name, league):
        h_data = EURO_DB[league][h_name]
        a_data = EURO_DB[league][a_name]
        
        # Logica di scontro stili (esempio: Pressing Alto soffre Contropiede)
        bonus_h = 1.10 # Vantaggio casa
        if h_data['style'] == "Pressing Alto" and a_data['style'] == "Attacco/Contropiede":
            bonus_h -= 0.05 # Malus tattico
            
        total = (h_data['p'] * bonus_h) + a_data['p']
        p1 = (h_data['p'] * bonus_h) / total
        p2 = a_data['p'] / total
        px = 0.24
        
        norm = p1 + px + p2
        return {"1": p1/norm, "X": px/norm, "2": p2/norm, "score": f"{int(p1*4)}-{int(p2*3)}"}

# --- 3. CONFIGURAZIONE E STILE ---
st.set_page_config(page_title="AI TOTAL ANALYST", layout="wide")
st.markdown("""<style>
    .stApp {background: #0d1117;}
    .metric-card {background: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #30363d;}
    .verdetto-pro {font-size: 1.2rem; font-weight: bold; padding: 10px; border-radius: 5px; text-align: center;}
</style>""", unsafe_allow_html=True)

# --- 4. GESTIONE STATO (LISTA GIOCATE E ROI) ---
if 'bets' not in st.session_state: st.session_state.bets = []

# --- 5. INTERFACCIA ---
st.title("🏆 AI Football Command Center")

tab_cat, tab_list, tab_finanze = st.tabs(["📊 Catalogo Leghe", "📝 Schedina Corrente", "💰 Monitor ROI"])

# --- TABELLA CATALOGO ---
with tab_cat:
    selected_l = st.selectbox("Seleziona Campionato", list(EURO_DB.keys()))
    teams = list(EURO_DB[selected_l].keys())
    
    st.subheader(f"Analisi Approfondita: {selected_l}")
    for i in range(0, len(teams)-1, 2):
        h, a = teams[i], teams[i+1]
        res = NeuralAnalyst.deep_match_analysis(h, a, selected_l)
        
        with st.container():
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.markdown(f"### {h} vs {a}")
                st.write(f"🏠 Stile Casa: `{EURO_DB[selected_l][h]['style']}`")
                st.write(f"🚌 Stile Trasferta: `{EURO_DB[selected_l][a]['style']}`")
            with col2:
                fig = go.Figure(go.Bar(x=['1', 'X', '2'], y=[res['1'], res['X'], res['2']], marker_color=['#22c55e', '#6b7280', '#ef4444']))
                fig.update_layout(height=150, margin=dict(t=0,b=0,l=0,r=0), paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
                st.plotly_chart(fig, use_container_width=True)
            with col3:
                st.write("**Risultato AI:**")
                st.code(res['score'])
                if st.button("➕ Inserisci in Schedina", key=f"add_{h}"):
                    st.session_state.bets.append({"m": f"{h}-{a}", "p": res['1']})
                    st.toast("Aggiunto!")

# --- TABELLA SCHEDINA ---
with tab_list:
    st.subheader("I tuoi pronostici selezionati")
    if not st.session_state.bets:
        st.info("La tua schedina è vuota.")
    else:
        for b in st.session_state.bets:
            st.markdown(f'<div class="metric-card">⚽ {b["m"]} | Probabilità Vittoria Casa: **{b["p"]:.1%}**</div>', unsafe_allow_html=True)
        if st.button("Svuota Schedina"):
            st.session_state.bets = []
            st.rerun()

# --- TABELLA ROI (FINANZE) ---
with tab_finanze:
    st.subheader("Performance Investimento")
    c1, c2, c3 = st.columns(3)
    c1.metric("Capitale Iniziale", "1000€")
    c2.metric("Profitto Netto", "+245€", "+12%")
    c3.metric("Win Rate AI", "68%", "Top Performance")
    
    # Grafico ROI finto per visualizzazione
    st.line_chart([1000, 1050, 1020, 1100, 1150, 1245])
