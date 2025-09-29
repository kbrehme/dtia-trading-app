import streamlit as st
import time
from dtia_trading_alerts import run_full_strategy

st.set_page_config(page_title="DTIA Trading Alerts", layout="centered")
st.title("📈 DTIA Trading Assistant")

# Query-Params prüfen (funktioniert nur nach vollständigem App-Load)
query_params = st.query_params
auto_run = query_params.get("run", ["false"])[0].lower() == "true"

# Session-Trigger setzen, um doppelten Run zu vermeiden
if 'already_ran' not in st.session_state:
    st.session_state['already_ran'] = False

# Automatischer Trigger (nur einmal)
if auto_run and not st.session_state['already_ran']:
    st.info("🚀 Automatischer Run wird vorbereitet...")
    with st.spinner("Strategie wird ausgeführt..."):
        time.sleep(2)  # Warten bis Session vollständig geladen
        run_full_strategy()
    st.success("✅ Strategie wurde automatisch ausgeführt und per Telegram gesendet.")
    st.session_state['already_ran'] = True
else:
    st.write("Willkommen! Du kannst die tägliche Strategie manuell starten:")

    if st.button("🚀 Strategie jetzt manuell ausführen"):
        run_full_strategy()
        st.success("✅ Strategie wurde ausgeführt und per Telegram gesendet.")
