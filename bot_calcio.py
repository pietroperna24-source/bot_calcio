import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

# --- CONFIGURAZIONE E DATABASE SQUADRE ---
# (Mantieni il database COMPLETO_DB dei messaggi precedenti)

class DirettaScraper:
    @staticmethod
    def get_today_matches():
        """Scansiona Diretta.it per trovare i match di oggi"""
        url = "https://www.diretta.it/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        try:
            # Nota: Diretta.it carica i dati via JS. 
            # In mancanza di Selenium, analizziamo i metadati o i blocchi HTML statici disponibili.
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Cerchiamo i blocchi delle partite (ID e classi variano spesso su Diretta)
            matches = []
            
            # Esempio di logica di estrazione (va adattata se il sito cambia struttura)
            # Cerchiamo i nomi delle squadre nei tag che contengono solitamente i match
            for row in soup.select(".event__match"):
                home = row.select_one(".event__participant--home").text.strip()
                away = row.select_one(".event__participant--away").text.strip()
                league = "Europa" # Valore di default se non rilevato
                
                matches.append({
                    "lega": league,
                    "home": home,
                    "away": away,
                    "ora": "Live/Oggi"
                })
            
            return matches
        except Exception as e:
            st.error(f"Errore connessione Diretta.it: {e}")
            return []

# --- INTERFACCIA STREAMLIT ---
st.title("🏟️ AI Live Scraper - Diretta.it")

if st.button("🔄 AGGIORNA PALINSESTO DA DIRETTA.IT"):
    with st.spinner("Connessione ai server di Diretta.it in corso..."):
        today_events = DirettaScraper.get_today_matches()
        
        if not today_events:
            st.warning("⚠️ Non è stato possibile leggere i dati live. Il sito potrebbe essere protetto. Utilizzo palinsesto simulato basato su database interno.")
            # Fallback su match casuali se lo scraping fallisce
            today_events = [
                {"lega": "Serie A", "home": "Inter", "away": "Milan", "ora": "20:45"},
                {"lega": "Premier League", "home": "Arsenal", "away": "Man City", "ora": "17:30"}
            ]

        for match in today_events:
            with st.container():
                st.markdown(f"""
                <div style="background: #161b22; padding: 15px; border-radius: 10px; border-left: 5px solid #58a6ff; margin-bottom: 10px;">
                    <small>{match['lega']}</small>
                    <h3>{match['home']} vs {match['away']}</h3>
                    <p>Stato: <b>{match['ora']}</b></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Qui inserisci la tua logica AI per calcolare le probabilità (come visto nei codici precedenti)
                st.write("🤖 *Analisi AI in corso per questo evento...*")
                st.divider()
