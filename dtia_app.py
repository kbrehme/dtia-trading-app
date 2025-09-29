
import streamlit as st
from dtia_trading_alerts import run_full_strategy

st.set_page_config(page_title="DTIA Trading Picks", layout="centered")

st.title("📈 DTIA Trading Alerts")
st.markdown("**Top 3 Picks täglich für US, DAX & Krypto**")

if st.button("🚀 Neue Signale abrufen & per Telegram senden"):
    run_full_strategy()
    st.success("✅ Signale wurden berechnet & gesendet!")
