import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import math

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="AI NEURAL ANALYST - OFFLINE", page_icon="🧠", layout="wide")

# --- LOGICA DI CALCOLO NEURALE ---
class NeuralProcessor:
    @staticmethod
    def analyze_data(o1, ox, o2):
        # Calcolo del Margine (Aggio)
        margin = (1/o1) + (1/ox) + (1/o2)
        # Probabilità reali (Normalizzate)
        p1 = (1/o1) / margin
        px = (1/ox) / margin
        p2 = (1/o2) / margin
        
        # Fair Odds (Quote eque senza profitto bookmaker)
        fair_o1 = 1/p1
        fair_ox = 1/px
        fair_o2 = 1/p2
        
        return {
            "p1": p1, "px": px, "p2": p2,
            "fair": [fair_o1, fair_ox, fair_o2],
            "aggio": (margin - 1) * 100
        }

# --- CSS PER PULIZIA INTERFACCIA ---
st.markdown("""
    <style>
    #MainMenu, header, footer {visibility: hidden; display: none !important;}
    .stApp { background: #0e1117; }
    .main-card { 
        background: #161b22; border-radius: 15px; padding: 25px; 
        border: 1px solid #30363d; margin-bottom: 20px;
    }
    .stNumberInput div div input { background-color: #1f2937 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- INTERFACCIA PRINCIPALE ---
st.title("🧠 AI Neural Analyst")
st.subheader("Inserimento manuale dati per analisi istantanea")

with st.container():
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    col_in1, col_in2, col_in3 = st.columns(3)
    
    with col_in1:
        o1 = st.number_input("Quota Segno 1", min_value=1.01, value=2.10, step=0.01)
    with col_in2:
        ox = st.number_input("Quota Segno X", min_value=1.01, value=3.40, step=0.01)
    with col_in3:
        o2 = st.number_input("Quota Segno 2", min_value=1.01, value=3.80, step=0.01)
    
    st.markdown('</div>', unsafe_allow_html=True)

# --- ELABORAZIONE AI ---
if st.button("🚀 ELABORA VALUTAZIONE NEURALE"):
    data = NeuralProcessor.analyze_data(o1, ox, o2)
    
    # --- VISUALIZZAZIONE RISULTATI ---
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.write("### 📊 Probabilità Reali")
        
        # Grafico a Torta
        fig = go.Figure(data=[go.Pie(
            labels=['Vittoria Casa (1)', 'Pareggio (X)', 'Vittoria Trasferta (2)'],
            values=[data['p1'], data['px'], data['p2']],
            hole=.4,
            marker_colors=['#22c55e', '#6b7280', '#ef4444']
        )])
        fig.update_layout(
            showlegend=True, 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white"),
            margin=dict(t=0, b=0, l=0, r=0)
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="main-card">', unsafe_allow_html=True)
        st.write("### 🤖 Verdetto AI")
        
        # Calcolo Value Bet
        # Se la probabilità reale è più alta di quella implicita nella quota, c'è valore
        st.metric("Aggio Bookmaker", f"{data['aggio']:.2f}%", delta_color="inverse")
        
        st.write("---")
        st.write("**Quote Eque Calcolate (Fair Odds):**")
        st.write(f"1: :green[{data['fair'][0]:.2f}] | X: :gray[{data['fair'][1]:.2f}] | 2: :red[{data['fair'][2]:.2f}]")
        
        st.write("---")
        # Logica di consiglio
        if data['aggio'] > 10:
            st.warning("⚠️ ATTENZIONE: Questo bookmaker sta applicando un aggio molto alto (>10%). Le quote non sono convenienti.")
        
        # Valutazione Segno 1
        diff = (o1 * data['p1']) - 1
        if diff > 0.05:
            st.success(f"✅ VALORE TROVATO SUL SEGNO 1: +{diff:.1%}")
        elif data['p1'] > 0.60:
            st.info("🔥 PROBABILITÀ ELEVATA SEGNO 1 (Oltre 60%)")
        else:
            st.write("❌ Nessun valore matematico evidente al momento.")
            
        st.markdown('</div>', unsafe_allow_html=True)

    # --- TABELLA DI CONFRONTO ---
    st.write("### 🔍 Tabella di Riepilogo")
    df_res = pd.DataFrame({
        "Evento": ["Vittoria Casa (1)", "Pareggio (X)", "Vittoria Trasferta (2)"],
        "Tua Quota": [o1, ox, o2],
        "Quota Equa AI": [round(x, 2) for x in data['fair']],
        "Probabilità Reale": [f"{round(x*100, 1)}%" for x in [data['p1'], data['px'], data['p2']]]
    })
    st.table(df_res)

else:
    st.info("Inserisci le quote sopra e clicca sul tasto per avviare l'intelligenza artificiale.")
