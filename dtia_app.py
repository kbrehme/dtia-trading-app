
import streamlit as st
from dtia_trading_alerts import run_yahoo_gainers_analysis
from modules.yahoo_scraper import get_yahoo_top_gainers
from modules.signal_debugger import debug_multiple_tickers

st.set_page_config(page_title="DTIA Yahoo Gainers", layout="centered")
st.title("📈 DTIA Yahoo Gainers Analyzer")

if "already_ran" not in st.session_state:
    st.session_state["already_ran"] = False

query_params = st.experimental_get_query_params()
auto_run = query_params.get("run", ["false"])[0].lower() == "true"

if auto_run and not st.session_state["already_ran"]:
    st.info("🚀 Automatischer Run über ?run=true")
    run_yahoo_gainers_analysis()
    st.success("✅ Analyse abgeschlossen und an Telegram gesendet.")
    st.session_state["already_ran"] = True
else:
    st.write("Willkommen zur täglichen Yahoo-Gainers-Analyse!")

    if st.button("🚀 Jetzt Analyse starten"):
        run_yahoo_gainers_analysis()
        st.success("✅ Analyse abgeschlossen und an Telegram gesendet.")

# Neue Debug-Kachel
with st.expander("🔍 Debug-Analyse der Top Gainers anzeigen"):
    st.info("Diese Analyse zeigt, warum bestimmte Aktien als Signal abgelehnt oder akzeptiert wurden.")
    tickers = get_yahoo_top_gainers(count=10)
    debug_data = debug_multiple_tickers(tickers)

    for stock in debug_data:
        st.subheader(f"📊 {stock['symbol']}")
        st.write(f"**RSI:** {stock['rsi']} | **ATR:** {stock['atr']} | **Volumen:** {stock['volume']}")
        if stock["valid"]:
            st.success("✅ Gültiges Signal erkannt!")
            st.write(f"Signalrichtung: **{stock.get('signal', 'Nicht erkannt')}**")
        else:
            st.error("❌ Kein Signal")
            st.write("Gründe:")
            for reason in stock["reasons"]:
                st.markdown(f"- {reason}")
