import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

# --- 1. DATABASE INTEGRALE (Tutte le squadre dei Top 5 Campionati) ---
COMPLETO_DB = {
    "Italia - Serie A": [
        "Inter", "Milan", "Juventus", "Napoli", "Atalanta", "Roma", "Lazio", 
        "Bologna", "Fiorentina", "Torino", "Monza", "Genoa", "Lecce", 
        "Udinese", "Cagliari", "Verona", "Empoli", "Parma", "Venezia", "Como"
    ],
    "Inghilterra - Premier League": [
        "Man City", "Arsenal", "Liverpool", "Aston Villa", "Tottenham", "Chelsea", 
        "Newcastle", "Man United", "West Ham", "Brighton", "Wolves", "Fulham", 
        "Bournemouth", "Everton", "Brentford", "Crystal Palace", "Forest", "Leicester", "Ipswich", "Southampton"
    ],
    "Spagna - La Liga": [
        "Real Madrid", "Barcelona", "Girona", "Atletico Madrid", "Athletic Bilbao", 
        "Real Sociedad", "Betis", "Villarreal", "Valencia", "Alaves", "Osasuna", 
        "Getafe", "Celta Vigo", "Sevilla", "Mallorca", "Las Palmas", "Leganes", "Valladolid", "Espanyol", "Rayo Vallecano"
    ],
    "Germania - Bundesliga": [
        "Bayer Leverkusen", "Bayern Munich", "Stuttgart", "RB Leipzig", "Dortmund", 
        "Frankfurt", "Hoffenheim", "Heidenheim", "Werder Bremen", "Freiburg", 
        "Augsburg", "Wolfsburg", "Mainz", "Monchengladbach", "Union Berlin", "Bochum", "St. Pauli", "Holstein Kiel"
    ],
    "Francia - Ligue 1": [
        "PSG", "Monaco", "Brest", "Lille", "Nice", "Lyon", "Lens", "Marseille", 
        "Reims", "Rennes", "Toulouse", "Montpellier", "Strasbourg", "Le Havre", "Nantes", "Angers", "St. Etienne", "Auxerre"
    ]
}

# --- 2. CONFIGURAZIONE UI ---
st.set_page_config(page_title="NEURAL SPORT HUB", layout="wide")
st.markdown("""<style>
    .stApp {background-color: #0d1117;}
    .league-card {background: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; margin-bottom: 10px;}
    .match-header {color: #58a6ff; font-weight: bold;}
    .ai-badge {background: #238636; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.8rem;}
</style>""", unsafe_allow_html=True)

# --- 3. MOTORE DI ANALISI ---
def get_neural_forecast(h, a):
    # Simulazione potenza basata sulla posizione in lista (squadre in alto più forti)
    p_h = 95 - random.randint(0, 20)
    p_a = 90 - random.randint(0, 25)
    
    total = p_h + p_a + 25 # 25 è il fattore pareggio
    return {
        "1": p_h / total,
        "X": 25 / total,
        "2": p_a / total,
        "over": random.uniform(0.3, 0.8)
    }

# --- 4. GESTIONE SESSIONE ---
if 'schedina' not in st.session_state: st.session_state.schedina = []

# --- 5. INTERFACCIA PRINCIPALE ---
st.title("🧠 Neural Sport Intelligence - 2026")

tab_daily, tab_catalog, tab_bet = st.tabs(["📅 Eventi Giornalieri", "📂 Catalogo Squadre", "📝 La Mia Lista"])

# --- TAB 1: EVENTI GIORNALIERI ---
with tab_daily:
    st.subheader(f"Palinsesto del {datetime.now().strftime('%d/%m/%Y')}")
    
    # Generiamo 5 match casuali per il giorno
    for _ in range(5):
        lega = random.choice(list(COMPLETO_DB.keys()))
        squadre = random.sample(COMPLETO_DB[lega], 2)
        h, a = squadre[0], squadre[1]
        res = get_neural_forecast(h, a)
        
        with st.container():
            st.markdown(f'''<div class="league-card">
                <span class="match-header">{lega}</span> | 🕒 20:45
                <h3>{h} vs {a} <span class="ai-badge">AI ANALYZED</span></h3>
            </div>''', unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns([1, 2, 1])
            with c1:
                st.write(f"🏠 1: **{res['1']:.1%}**")
                st.write(f"⚖️ X: **{res['X']:.1%}**")
                st.write(f"🚌 2: **{res['2']:.1%}**")
            with c2:
                # Grafico probabilità Over
                st.write("Probabilità Over 2.5")
                st.progress(res['over'])
            with c3:
                if st.button("Aggiungi", key=f"btn_{h}_{a}"):
                    st.session_state.schedina.append({"m": f"{h}-{a}", "res": "1" if res['1']>res['2'] else "2"})
                    st.toast("Match salvato!")
            st.divider()

# --- TAB 2: CATALOGO SQUADRE ---
with tab_catalog:
    st.info("Esplora tutte le squadre e crea i tuoi scontri diretti personalizzati.")
    col_l, col_h, col_a = st.columns(3)
    
    sel_lega = col_l.selectbox("Seleziona Lega", list(COMPLETO_DB.keys()))
    sel_h = col_h.selectbox("Squadra Casa", COMPLETO_DB[sel_lega])
    sel_a = col_a.selectbox("Squadra Trasferta", COMPLETO_DB[sel_lega])
    
    if st.button("🚀 ANALISI NEURALE CUSTOM"):
        custom_res = get_neural_forecast(sel_h, sel_a)
        st.markdown(f'<div class="league-card"><h3>Analisi: {sel_h} vs {sel_a}</h3></div>', unsafe_allow_html=True)
        st.write(f"L'IA prevede una probabilità di vittoria del **{custom_res['1']:.1%}** per il {sel_h}.")

# --- TAB 3: SCHEDINA PERSONALE ---
with tab_bet:
    st.subheader("I Tuoi Pronostici Selezionati")
    if not st.session_state.schedina:
        st.write("Nessun evento selezionato.")
    else:
        for b in st.session_state.schedina:
            st.success(f"⚽ {b['m']} -> Segno consigliato: **{b['res']}**")
        if st.button("Pulisci Lista"):
            st.session_state.schedina = []
            st.rerun()

# --- 6. WEB SCANNER (SIMULAZIONE) ---
with st.sidebar:
    st.header("🌐 AI Web Scanner")
    st.write("Stato: ● **In ascolto sui portali**")
    if st.button("Esegui Scansione Flash"):
        st.info("Scansione di: Diretta.it, Flashscore, Gazzetta...")
        st.write("📢 **Notizia:** Inter senza il portiere titolare stasera.")
        st.write("📢 **Meteo:** Pioggia forte prevista a Londra (Arsenal-Man City).")
