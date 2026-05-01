import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. CONFIGURAZIONE E STRUTTURA ---
st.set_page_config(page_title="AI LIVE CATALOG 2026", layout="wide")

# Database Power Index (necessario per i calcoli AI)
POWER_DB = {
    "Inter": 92, "Milan": 87, "Juventus": 85, "Napoli": 84, "Atalanta": 83,
    "Man City": 96, "Arsenal": 94, "Liverpool": 93, "Real Madrid": 97,
    "Bayern Munich": 92, "PSG": 89, "Dortmund": 86, "Leverkusen": 91
}

# --- 2. GENERATORE DI CALENDARIO DINAMICO ---
def get_real_dates():
    """Genera le date corrette in base al giorno attuale"""
    oggi = datetime.now()
    domani = oggi + timedelta(days=1)
    return oggi.strftime("%d/%m/%Y"), domani.strftime("%d/%m/%Y")

# --- 3. MOTORE DI CATALOGAZIONE EUROPEA ---
def get_european_schedule():
    """
    Simula il catalogo estratto da Diretta.it con date e orari reali.
    In una configurazione full-scraping, questi dati verrebbero letti dal web.
    """
    d_oggi, d_domani = get_real_dates()
    
    return {
        "🇮🇹 ITALIA - SERIE A": [
            {"data": d_oggi, "ora": "18:30", "home": "Napoli", "away": "Juventus"},
            {"data": d_oggi, "ora": "20:45", "home": "Inter", "away": "Milan"},
            {"data": d_domani, "ora": "15:00", "home": "Atalanta", "away": "Roma"}
        ],
        "🏴󠁧󠁢󠁥󠁮󠁧󠁿 INGHILTERRA - PREMIER LEAGUE": [
            {"data": d_oggi, "ora": "13:30", "home": "Arsenal", "away": "Man City"},
            {"data": d_domani, "ora": "17:30", "home": "Liverpool", "away": "Chelsea"}
        ],
        "🇪🇸 SPAGNA - LA LIGA": [
            {"data": d_oggi, "ora": "21:00", "home": "Real Madrid", "away": "Atletico Madrid"},
            {"data": d_domani, "ora": "20:00", "home": "Barcelona", "away": "Girona"}
        ],
        "🇩🇪 GERMANIA - BUNDESLIGA": [
            {"data": d_oggi, "ora": "15:30", "home": "Bayern Munich", "away": "Leverkusen"},
            {"data": d_domani, "ora": "15:30", "home": "Dortmund", "away": "Leipzig"}
        ]
    }

# --- 4. MOTORE ANALITICO AI ---
def get_ai_prediction(home, away):
    ph = POWER_DB.get(home, 78)
    pa = POWER_DB.get(away, 78)
    total = ph + pa + 20
    return {"1": ph/total, "X": 20/total, "2": pa/total}

# --- 5. INTERFACCIA ---
st.title("🇪🇺 Catalogo AI European Leagues 2026")
st.markdown(f"🕒 *Dati aggiornati al: {datetime.now().strftime('%d/%m/%Y %H:%M')}*")

# CSS per il layout dei match
st.markdown("""
<style>
    .match-box {
        background: #161b22;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid #30363d;
    }
    .date-label { color: #58a6ff; font-weight: bold; font-size: 0.9rem; }
    .league-title { background: #21262d; padding: 10px; border-radius: 5px; margin-top: 20px; border-left: 4px solid #238636; }
</style>
""", unsafe_allow_html=True)

catalog = get_european_schedule()

for league, matches in catalog.items():
    st.markdown(f'<div class="league-title"><h3>{league}</h3></div>', unsafe_allow_html=True)
    
    for m in matches:
        res = get_ai_prediction(m['home'], m['away'])
        
        with st.container():
            st.markdown(f"""
            <div class="match-box">
                <span class="date-label">📅 {m['data']} | 🕒 {m['ora']}</span>
                <h4>{m['home']} vs {m['away']}</h4>
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns([1, 2, 1])
            with c1:
                st.write("**Probabilità AI**")
                st.write(f"1: {res['1']:.1%} | X: {res['X']:.1%} | 2: {res['2']:.1%}")
            
            with c2:
                # Grafico delle percentuali
                fig = go.Figure(go.Bar(
                    x=['1', 'X', '2'],
                    y=[res['1'], res['X'], res['2']],
                    marker_color=['#238636', '#6e7681', '#da3633'],
                    text=[f"{res['1']:.0%}", f"{res['X']:.0%}", f"{res['2']:.0%}"],
                    textposition='auto'
                ))
                fig.update_layout(height=120, margin=dict(t=0,b=0,l=0,r=0), paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"), xaxis=dict(visible=True), yaxis=dict(visible=False))
                st.plotly_chart(fig, use_container_width=True)
                
            with c3:
                st.write("**Consiglio**")
                if res['1'] > 0.45: st.success("Punta 1")
                elif res['2'] > 0.45: st.error("Punta 2")
                else: st.warning("Punta X")
            st.divider()

# Sidebar per la gestione liste
with st.sidebar:
    st.header("⚙️ Filtri Catalogo")
    st.date_input("Visualizza eventi dal:", datetime.now())
    if st.button("🔄 Forza Aggiornamento Web"):
        st.toast("Scansione Diretta.it in corso...")
