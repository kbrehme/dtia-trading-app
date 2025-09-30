
import streamlit as st
from dtia_trading_alerts import run_yahoo_gainers_analysis, get_debug_logs

st.set_page_config(page_title="DTIA Trading Alerts", layout="centered")
st.title("📈 DTIA Trading Assistant")

if st.button("🚀 Signale jetzt analysieren"):
    run_yahoo_gainers_analysis()
    st.success("✅ Analyse abgeschlossen und Signale gesendet.")

# Genauere Informationen anzeigen
debug_data = get_debug_logs()

if debug_data:
    debug_data.sort(key=lambda x: not x.get('valid', False))
    st.markdown("---")
    st.subheader("🧠 Genauere Informationen zu analysierten Tickers")

    # Scrollbare Box
    with st.container():
        with st.expander("📋 Alle analysierten Ticker anzeigen", expanded=True):
            st.markdown(
                "<div style='height: 400px; overflow-y: auto; padding-right:10px;'>",
                unsafe_allow_html=True
            )
            for entry in debug_data:
                symbol = entry.get("symbol", "N/A")
                valid = entry.get("valid", False)
                rsi = entry.get("rsi", "–")
                atr = entry.get("atr", "–")
                vol = entry.get("volume", "–")
                direction = entry.get("direction", "–")
                reasons = entry.get("reasons", [])

                st.markdown(f"""
<div style="border:1px solid #444; border-radius:8px; padding:10px; margin-bottom:12px; background-color: {'#1f1f1f'};">
<h4>🔍 {symbol}</h4>
<b>Status:</b> {"✅ <span style='color:lightgreen'>Gültig</span>" if valid else "❌ <span style='color:#ff6961'>Nicht gültig</span>"}  
<b>Signalrichtung:</b> {direction}  
📉 <b>RSI:</b> {rsi}  📊 <b>ATR:</b> {atr}  📦 <b>Volumen:</b> {vol}

{"<br><b>Ablehnungsgründe:</b><ul>" + "".join([f"<li>{r}</li>" for r in reasons]) + "</ul>" if not valid else ""}
</div>
""", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)
