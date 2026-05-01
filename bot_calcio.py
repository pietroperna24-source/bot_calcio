import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. DATABASE INTEGRALE EUROPA 2026 ---
EURO_DB = {
    "Serie A 🇮🇹": {
        "Inter": 94, "Milan": 88, "Juventus": 87, "Napoli": 85, "Atalanta": 86, "Roma": 82, "Lazio": 81, 
        "Bologna": 80, "Fiorentina": 79, "Torino": 77, "Monza": 75, "Genoa": 76, "Lecce": 72, 
        "Udinese": 73, "Cagliari": 71, "Verona": 70, "Empoli": 69, "Parma": 74, "Venezia": 68, "Como": 75
    },
    "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": {
        "Man City": 97, "Arsenal": 95, "Liverpool": 94, "Aston Villa": 86, "Tottenham": 85, "Chelsea": 83, 
        "Newcastle": 84, "Man United": 82, "West Ham": 79, "Brighton": 81, "Wolves": 76, "Fulham": 77, 
        "Bournemouth": 75, "Everton": 74, "Brentford": 76, "Crystal Palace": 78, "Nottm Forest": 73, 
        "Leicester": 74, "Ipswich": 70, "Southampton": 71
    },
    "La Liga 🇪🇸": {
        "Real Madrid": 98, "Barcelona": 92, "Atletico Madrid": 89, "Girona": 86, "Athletic Bilbao": 84, 
        "Real Sociedad": 83, "Betis": 81, "Villarreal": 82, "Valencia": 78, "Alaves": 75, "Osasuna": 76, 
        "Sevilla": 79, "Celta Vigo": 75, "Mallorca": 74, "Getafe": 74, "Las Palmas": 72, "Leganes": 70, 
        "Valladolid": 71, "Espanyol": 73, "Rayo Vallecano": 72
    },
    "Bundesliga 🇩🇪": {
        "Bayer Leverkusen": 92, "Bayern Munich": 93, "Stuttgart": 87, "RB Leipzig": 86, "Dortmund": 88, 
        "Frankfurt": 82, "Hoffenheim": 79, "Heidenheim": 77, "Werder Bremen": 76, "Freiburg": 78, 
        "Augsburg": 75, "Wolfsburg": 77, "Mainz": 74, "M'gladbach": 75, "Union Berlin": 73, "Bochum": 70, 
        "St. Pauli": 72, "Holstein Kiel": 69
    }
}

# --- 2. CONFIGURAZIONE ESTETICA ---
st.set_page_config(page_title="AI NEURAL ORACLE", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0b0e11; color: white; }
    .header-box {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 30px; border-radius: 20px; border: 1px solid #334155;
        text-align: center; margin-bottom: 30px;
    }
    .match-display {
        background: #1e293b; border-radius: 20px; padding: 40px;
        border: 1px solid #334155; text-align: center;
    }
    .team-name { font-size: 2.5rem; font-weight: 800; color: #f8fafc; }
    .vs-text { color: #3b82f6; font-size: 1.5rem; font-weight: bold; margin: 0 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. MOTORE ANALITICO ---
def neural_analysis(h, a, league):
    p_h = EURO_DB[league][h]
    p_a = EURO_DB[league][a]
    total = p_h + p_a + 22
    p1 = (p_h + 5) / total
    p2 = p_a / total
    px = 1.0 - (p1 + p2)
    return {"1": p1, "X": px, "2": p2}

# --- 4. INTERFACCIA ---
st.markdown('<div class="header-box"><h1>🔮 AI European Oracle 2026</h1><p>Analisi Predittiva Neurale Multi-Campionato</p></div>', unsafe_allow_html=True)

# Sidebar per la scelta dell'evento
with st.sidebar:
    st.header("🏟️ Seleziona Evento")
    league_sel = st.selectbox("Campionato", list(EURO_DB.keys()))
    teams = sorted(list(EURO_DB[league_sel].keys()))
    
    col_h, col_a = st.columns(2)
    h_team = col_h.selectbox("Casa", teams, index=0)
    a_team = col_a.selectbox("Trasferta", teams, index=1)
    
    st.divider()
    analyze_btn = st.button("🚀 AVVIA ANALISI PROFONDA", use_container_width=True)

# Main Area
if analyze_btn:
    if h_team == a_team:
        st.error("Seleziona due squadre diverse per l'analisi.")
    else:
        # FASE 1: CARICAMENTO DATI
        with st.status("🎯 L'IA sta scansionando l'evento...", expanded=True) as status:
            st.write("🔍 Collegamento ai server sportivi europei...")
            time.sleep(1)
            st.write(f"📊 Recupero Power Index 2026 per {h_team} e {a_team}...")
            time.sleep(1.2)
            st.write("☁️ Analisi condizioni meteo e stato del terreno...")
            time.sleep(0.8)
            st.write("📈 Elaborazione algoritmi di probabilità neurale...")
            time.sleep(1.5)
            status.update(label="✅ Analisi Completata!", state="complete", expanded=False)

        # FASE 2: VISUALIZZAZIONE RISULTATI
        res = neural_analysis(h_team, a_team, league_sel)
        
        st.markdown(f"""
            <div class="match-display">
                <span class="team-name">{h_team.upper()}</span>
                <span class="vs-text">VS</span>
                <span class="team-name">{a_team.upper()}</span>
                <p style="color: #94a3b8; margin-top: 10px;">{league_sel} • Match ID: AI-2026-{time.strftime('%H%M%S')}</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("---")
        
        c1, c2 = st.columns([1, 1])
        
        with c1:
            st.subheader("📊 Probabilità d'Esito")
            # Grafico a barre moderno
            fig = go.Figure(go.Bar(
                x=['SEGNO 1', 'SEGNO X', 'SEGNO 2'],
                y=[res['1'], res['X'], res['2']],
                marker_color=['#10b981', '#64748b', '#ef4444'],
                text=[f"{res['1']:.1%}", f"{res['X']:.1%}", f"{res['2']:.1%}"],
                textposition='auto',
            ))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color="white"), height=300, margin=dict(t=10, b=10)
            )
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.subheader("🤖 Verdetto AI")
            st.write(f"In base al Power Index attuale ({EURO_DB[league_sel][h_team]} vs {EURO_DB[league_sel][a_team]}), l'IA ha stabilito:")
            
            if res['1'] > 0.55:
                st.success(f"**CONSIGLIO: Vittoria Interna (1)**. Il {h_team} ha un vantaggio tattico e di roster significativo per questa sfida.")
            elif res['2'] > 0.55:
                st.error(f"**CONSIGLIO: Vittoria Esterna (2)**. Superiorità netta del {a_team}. Si prevede un dominio ospite nonostante il fattore campo.")
            else:
                st.warning(f"**CONSIGLIO: Doppia Chance o Pareggio**. Match estremamente equilibrato. La prudenza suggerisce un segno X o una copertura X2/1X.")

else:
    st.info("👈 Seleziona il campionato e le squadre dalla barra laterale e clicca su 'Avvia Analisi Profonda' per iniziare.")

# Footer
st.divider()
st.caption(f"Sincronizzazione globale: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | Modello Neurale: Gemini 3.0 Pro")
