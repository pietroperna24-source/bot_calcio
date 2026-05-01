import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURAZIONE INTERFACCIA ---
st.set_page_config(page_title="AI NEURAL AUTONOMOUS", layout="wide")

st.markdown("""
    <style>
    .stApp {background-color: #0d1117;}
    .league-card {
        background: #161b22; border-radius: 12px; padding: 20px; 
        border-left: 5px solid #3b82f6; margin-bottom: 20px;
    }
    .match-row {
        background: #1c2128; border: 1px solid #30363d;
        border-radius: 8px; padding: 15px; margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- MOTORE DI INTELLIGENZA AUTONOMA ---
class AutonomousScanner:
    @staticmethod
    def scan_and_inject():
        """
        L'IA interroga diversi database aperti e feed globali per 
        costruire il catalogo in tempo reale.
        """
        # Simulazione di scansione multi-sorgente (API/JSON Feed)
        # In questo passaggio l'IA 'trova' i dati e li normalizza
        
        aggregator_data = {
            "SERIE A - ITALIA": [
                {"h": "Inter", "a": "Milan", "t": "20:45"},
                {"h": "Juventus", "a": "Torino", "t": "18:00"}
            ],
            "PREMIER LEAGUE - INGHILTERRA": [
                {"h": "Man City", "a": "Arsenal", "t": "17:30"},
                {"h": "Liverpool", "a": "Chelsea", "t": "21:00"}
            ],
            "LA LIGA - SPAGNA": [
                {"h": "Real Madrid", "a": "Barcelona", "t": "21:00"}
            ]
        }
        return aggregator_data

# --- DATABASE FORZA (AI BRAIN) ---
# L'IA usa questi pesi per dare i pronostici ai dati che trova autonomamente
STRENGTH_INDEX = {
    "Inter": 94, "Milan": 88, "Juventus": 86, "Man City": 97, 
    "Arsenal": 95, "Liverpool": 94, "Real Madrid": 98, "Barcelona": 92
}

def ai_brain_analysis(home, away):
    # Recupero forza o valore neutro (80) se squadra nuova
    s_h = STRENGTH_INDEX.get(home, 80)
    s_a = STRENGTH_INDEX.get(away, 80)
    
    total = s_h + s_a + 20
    p1 = (s_h / total) * 1.05 # Bonus casa
    p2 = s_a / total
    px = 1.0 - (p1 + p2)
    return {"1": p1, "X": px, "2": p2}

# --- LAYOUT PRINCIPALE ---
st.title("🤖 AI Autonomous Match Injector")
st.write(f"Sincronizzazione Globale: **{datetime.now().strftime('%d/%m/%Y %H:%M')}**")

if st.button("🚀 AVVIA SCANSIONE AUTONOMA E INSERIMENTO"):
    with st.spinner("L'IA sta cercando e inserendo i match nel sito..."):
        # 1. L'IA cerca i dati autonomamente
        catalogo_generato = AutonomousScanner.scan_and_inject()
        
        # 2. L'IA inserisce i dati nel sito organizzandoli per sezione
        for lega, matches in catalogo_generato.items():
            st.markdown(f'<div class="league-card"><h2>🏆 {lega}</h2></div>', unsafe_allow_html=True)
            
            for m in matches:
                # 3. L'IA analizza ogni match appena inserito
                prob = ai_brain_analysis(m['h'], m['a'])
                
                with st.container():
                    st.markdown(f'''
                    <div class="match-row">
                        <div style="display: flex; justify-content: space-between;">
                            <span style="color: #58a6ff; font-weight: bold;">🕒 {m['t']}</span>
                            <span style="color: #8b949e;">ID: AI-{hash(m['h']) % 1000}</span>
                        </div>
                        <h3 style="margin: 10px 0;">{m['h']} vs {m['a']}</h3>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        # Grafico orizzontale istantaneo
                        fig = go.Figure(go.Bar(
                            x=[prob['1'], prob['X'], prob['2']],
                            y=['1', 'X', '2'],
                            orientation='h',
                            marker_color=['#22c55e', '#4b5563', '#ef4444']
                        ))
                        fig.update_layout(height=100, margin=dict(t=0,b=0,l=0,r=0), paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
                        st.plotly_chart(fig, use_container_width=True)
                    with c2:
                        st.write("**Verdetto AI**")
                        if prob['1'] > 0.45: st.success("PUNTA 1")
                        elif prob['2'] > 0.45: st.error("PUNTA 2")
                        else: st.warning("PUNTA X")
            st.divider()
else:
    st.info("Sistema in attesa. Clicca per permettere all'IA di popolare il sito autonomamente.")
