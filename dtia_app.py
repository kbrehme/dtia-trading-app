import streamlit as st
from dtia_trading_alerts import run_full_strategy

st.set_page_config(page_title="Tradingkid", layout="centered")
st.title("📈 Tradingkid")

# Query-Parameter auslesen über neues API (ab Streamlit 1.34)
auto_run = st.query_params.get("run", ["false"])[0].lower() == "true"

if auto_run:
    st.info("🚀 Automatisierter Run gestartet...")
    run_full_strategy()
    st.success("✅ Strategie wurde automatisch ausgeführt und per Telegram versendet.")
else:
    st.write("Willkommen! Du kannst die tägliche Strategie manuell starten:")

    if st.button("🚀 Strategie jetzt manuell ausführen"):
        run_full_strategy()
        st.success("✅ Strategie wurde ausgeführt und per Telegram gesendet.")
