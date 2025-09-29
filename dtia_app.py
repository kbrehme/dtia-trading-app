
import streamlit as st
from dtia_trading_alerts import run_yahoo_gainers_analysis

st.set_page_config(page_title="Tradingkid", layout="centered")
st.title("📈 Tradingkid")

# Initialisierungsstatus
if "already_ran" not in st.session_state:
    st.session_state["already_ran"] = False

# Query-Parameter lesen
query_params = st.experimental_get_query_params()
auto_run = query_params.get("run", ["false"])[0].lower() == "true"

# Automatischer Start
if auto_run and not st.session_state["already_ran"]:
    st.info("🚀 Automatischer Run über ?run=true")
    run_yahoo_gainers_analysis()
    st.success("✅ Analyse abgeschlossen und an Telegram gesendet.")
    st.session_state["already_ran"] = True
else:
    st.write("Willkommen zur täglichen Yahoo-Gainers-Analyse!")
    st.markdown("Klicke unten, um die Analyse sofort zu starten:")

    if st.button("🚀 Jetzt Analyse starten"):
        run_yahoo_gainers_analysis()
        st.success("✅ Analyse abgeschlossen und an Telegram gesendet.")
