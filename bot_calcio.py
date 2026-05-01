import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. DATABASE INTERNO (POWER INDEX 2026) ---
# Valori basati sulla forza stimata (100 = Top Mondiale, 50 = Media)
TEAMS_DATABASE = {
    "Serie A": {
        "Inter": 88, "Milan": 82, "Juventus": 81, "Napoli": 79, "Roma": 77,
        "Lazio": 76, "Atalanta": 80, "Fiorentina": 75, "Bologna": 74, "Torino": 72
    },
    "Premier League": {
        "Man City": 95, "Liverpool": 92, "Arsenal": 91, "Real Madrid": 94,
        "Bayern Munich": 89, "PSG": 87, "Barcelona": 85, "Bayer Leverkusen": 86
    }
}

# --- 2. CONFIGURAZIONE PAGINA E CSS ---
st.set_page_config(page_title="IA PREDICTOR PRO", layout="wide")

st.markdown("""
    <style>
    #MainMenu, header, footer {visibility: hidden; display: none !important;}
    .stApp { background: #0e1117; }
    .main-card { 
        background: #161b22; border-radius: 15px; padding: 25px; 
        border: 1px solid #30363d; margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MOTORE DI CALCOLO PREDITTIVO ---
class AIPredictor:
    @staticmethod
    def calculate_match(power_h, power_a, home_advantage=5):
        # Calcolo forza corretta dal fattore campo
        score_h = power_h + home_advantage
        score_a = power_a
        
        # Algoritmo di distribuzione probabilità
        total = score_h + score_a
        win_h = (score_h / total) * 1.10 # Correzione aggressività casa
        win_a = (score_a / total) * 0.90
        draw = 1.0 - (win_h + win_a)
        
        # Normalizzazione se il pareggio è troppo basso
        if draw < 0.20: draw = 0.24
        
        # Ricalcolo per somma 100%
        final_total = win_h + win_a + draw
        return {
            "1": win_h / final_total,
            "X": draw / final_total,
            "2": win_a / final_total
        }

# --- 4. INTERFACCIA UTENTE ---
st.title("🤖 IA Neural Match Analyst (Database Integrato)")
st.write("L'intelligenza artificiale elabora i dati basandosi sul Power Index interno delle squadre.")

with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    
    with c1:
        league = st.selectbox("Seleziona Campionato", list(TEAMS_DATABASE.keys()))
    with c2:
        team_h = st.selectbox("Squadra in Casa", list(TEAMS_DATABASE[league].keys()))
    with c3:
        team_a = st.selectbox("Squadra in Trasferta", list(TEAMS_DATABASE[league].keys()))
    
    st.markdown('</div>', unsafe_allow_html=True)

if team_h == team_a:
    st.warning("Seleziona due squadre diverse per l'analisi.")
else:
    # --- ESECUZIONE AI ---
    ph = TEAMS_DATABASE[league][team_h]
    pa = TEAMS_DATABASE[league][team_a]
    
    res = AIPredictor.calculate_match(ph, pa)

    # --- RISULTATI ---
    col_res1, col_res2 = st.columns([1, 1])

    with col_res1:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.write(f"### 📊 Percentuali AI: {team_h} vs {team_a}")
        
        fig = go.Figure(data=[go.Pie(
            labels=[team_h, 'Pareggio', team_a],
            values=[res['1'], res['X'], res['2']],
            hole=.4,
            marker_colors=['#00ff00', '#555', '#ff4b4b']
        )])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), margin=dict(t=0,b=0,l=0,r=0))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_res2:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.write("### 🤖 Valutazione Tecnica")
        st.write(f"🔹 **Forza {team_h}:** {ph}/100")
        st.write(f"🔹 **Forza {team_a}:** {pa}/100")
        st.divider()
        
        # Verdetto dinamico
        if res['1'] > res['2'] and res['1'] > 0.50:
            st.success(f"🏆 PRONOSTICO: Forte vantaggio per **{team_h}**")
        elif res['2'] > res['1'] and res['2'] > 0.50:
            st.success(f"🏆 PRONOSTICO: Forte vantaggio per **{team_a}**")
        else:
            st.info("⚖️ PRONOSTICO: Partita equilibrata (Possibile X)")
        
        st.write(f"📈 **Quota Equa Consigliata (1):** {1/res['1']:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)

# --- 5. TABELLA POWER INDEX ---
with st.expander("Visualizza Database Forza Squadre"):
    df_db = pd.DataFrame([
        {"Squadra": k, "Power Index": v, "Campionato": league} 
        for k, v in TEAMS_DATABASE[league].items()
    ])
    st.dataframe(df_db.sort_values("Power Index", ascending=False), use_container_width=True)
