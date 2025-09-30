
import streamlit as st
from dtia_trading_alerts import run_yahoo_gainers_analysis, get_debug_logs

st.set_page_config(page_title="DTIA Trading Alerts", layout="centered")
st.title("📈 DTIA Trading Assistant")

# Manuelle Strategieausführung
if st.button("🚀 Signale jetzt analysieren"):
    run_yahoo_gainers_analysis()
    st.success("✅ Analyse abgeschlossen und Signale gesendet.")

# Debugdaten anzeigen (jetzt: genauere Informationen)
debug_data = get_debug_logs()

if debug_data:
    st.markdown("---")
    st.subheader("🧠 Genauere Informationen zu analysierten Tickers")

    for entry in debug_data:
        symbol = entry.get("symbol", "N/A")
        st.markdown(f"### 🔍 {symbol}")
        st.markdown(f"""
        - **Gültig:** {'✅ Ja' if entry.get("valid") else '❌ Nein'}
        - **Signalrichtung:** {entry.get("direction", '–')}
        - **RSI:** {entry.get("rsi", '–')}
        - **ATR:** {entry.get("atr", '–')}
        - **Volumen:** {entry.get("volume", '–')}
        """)
        if not entry.get("valid") and entry.get("reasons"):
            st.markdown("**Ablehnungsgründe:**")
            for reason in entry["reasons"]:
                st.markdown(f"- {reason}")
