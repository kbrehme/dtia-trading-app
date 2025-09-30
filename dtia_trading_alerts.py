from modules.ticker_loader import get_us_tickers, get_dax_tickers, get_crypto_tickers
from modules.signal_analysis import generate_trade_signal
from modules.telegram_utils import send_telegram_alert
from datetime import datetime
import time

# Logs für WebUI
debug_logs_storage = []

def store_debug_log(entry):
    debug_logs_storage.append(entry)

def get_debug_logs():
    return debug_logs_storage

def run_yahoo_gainers_analysis():
    signals = []
    today = datetime.now().strftime("%d.%m.%Y")
    start_time = time.time()

    # 🔄 Ticker aus .txt laden
    markets = {
        "US": get_us_tickers(),
        "DAX": get_dax_tickers(),
        "Crypto": get_crypto_tickers()
    }

    for market_name, tickers in markets.items():
        for ticker in tickers:
            try:
                signal, log = generate_trade_signal(ticker)
                log["market"] = market_name
                store_debug_log(log)

                if signal:
                    signal["market"] = market_name
                    signals.append(signal)

            except Exception as e:
                store_debug_log({
                    "symbol": ticker,
                    "valid": False,
                    "market": market_name,
                    "reasons": [f"❌ Fehler: {str(e)}"]
                })

    # ⏱ Dauer
    duration = round(time.time() - start_time, 2)
    message = f"🚨 <b>DTIA Signalanalyse</b> – {today}\n⏱ Dauer: {duration}s\n\n"

    if not signals:
        message += "⚠️ Keine verwertbaren Signale gefunden."
    else:
        # 🔃 Gruppiere & sortiere Signale nach Score
        for market in ["US", "DAX", "Crypto"]:
            filtered = [s for s in signals if s.get("market") == market]
            if not filtered:
                message += f"📊 <b>{market}:</b>\n– Keine gültigen Signale\n\n"
                continue

            sorted_signals = sorted(filtered, key=lambda x: x.get("score", 0), reverse=True)

            message += f"📊 <b>{market}:</b>\n"
            for sig in sorted_signals[:3]:  # Top 3 pro Markt
                symbol = sig.get("symbol", "–")
                direction = sig.get("direction", "–")
                entry = sig.get("entry", "–")
                target = sig.get("target", "–")
                stop = sig.get("stop", "–")
                strength = sig.get("signal_strength", "–")
                message += (
                    f"{symbol} {direction} @ {entry} → 🎯 {target} | ⛔ {stop} {strength}\n"
                )
            message += "\n"

    # 📤 Telegram senden
    send_telegram_alert(message)
