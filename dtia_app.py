
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
    st.markdown("---")
    st.subheader("🧠 Genauere Informationen zu analysierten Tickers")

    # Sortiere nach gültigen Signalen oben
    debug_data.sort(key=lambda x: not x.get("valid", False))

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
                score = entry.get("score", None)
                reasons = entry.get("reasons", [])

                # Ampelfarbe nach Score
                if isinstance(score, int):
                    if score >= 5:
                        score_color = "🟢 Sehr stark"
                    elif score >= 3:
                        score_color = "🟡 Mittel"
                    else:
                        score_color = "🔴 Schwach"
                else:
                    score_color = "–"

                html = f"""
<div style="border:1px solid #444; border-radius:8px; padding:10px; margin-bottom:12px; background-color:#1f1f1f;">
<h4>🔍 {symbol}</h4>
<b>Status:</b> {"✅ <span style='color:lightgreen'>Gültig</span>" if valid else "❌ <span style='color:#ff6961'>Nicht gültig</span>"}<br>
<b>Signalrichtung:</b> {direction}<br>
💯 <b>Score:</b> {score if score is not None else "–"} ({score_color})<br>
📉 <b>RSI:</b> {rsi}  📊 <b>ATR:</b> {atr}  📦 <b>Volumen:</b> {vol}<br>
"""
                if not valid and reasons:
                    html += "<br><b>Ablehnungsgründe:</b><ul>"
                    for r in reasons:
                        html += f"<li>{r}</li>"
                    html += "</ul>"

                html += "</div>"

                st.markdown(html, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)
