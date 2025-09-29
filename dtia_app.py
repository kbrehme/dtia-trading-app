
import streamlit as st
from dtia_trading_alerts import run_full_strategy

st.set_page_config(page_title="DTIA Trading Alerts", layout="centered")
st.title("📈 DTIA Trading Assistant")

# Sicherstellen, dass die Strategie nur 1x automatisch ausgeführt wird
if "already_ran" not in st.session_state:
    st.session_state["already_ran"] = False

# Query-Parameter auslesen
query_params = st.experimental_get_query_params()
auto_run = query_params.get("run", ["false"])[0].lower() == "true"

# Automatischer Run
if auto_run and not st.session_state["already_ran"]:
    st.info("🚀 Automatischer Run aktiviert über ?run=true")
    run_full_strategy()
    st.success("✅ Strategie wurde automatisch ausgeführt und per Telegram gesendet.")
    st.session_state["already_ran"] = True
else:
    st.write("Willkommen! Du kannst die tägliche Strategie auch manuell starten:")

    if st.button("🚀 Strategie jetzt manuell ausführen"):
        run_full_strategy()
        st.success("✅ Strategie wurde ausgeführt und per Telegram gesendet.")
