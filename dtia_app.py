
import streamlit as st
from dtia_trading_alerts import run_full_strategy

st.set_page_config(page_title="DTIA Trading Alerts", layout="centered")

st.title("📈 DTIA Trading Assistant")

# Prüfe auf automatisierten Trigger via URL
query_params = st.experimental_get_query_params()()
auto_run = query_params.get("run", ["false"])[0].lower() == "true"

if auto_run:
    st.info("🚀 Automatisierter Run gestartet...")
    run_full_strategy()
    st.success("✅ Strategie wurde automatisch ausgeführt und per Telegram versendet.")
else:
    st.write("Willkommen! Du kannst die tägliche Strategie manuell starten:")

    if st.button("🚀 Strategie jetzt manuell ausführen"):
        run_full_strategy()
        st.success("✅ Strategie wurde ausgeführt und per Telegram gesendet.")
