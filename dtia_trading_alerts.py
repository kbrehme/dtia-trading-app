from modules.yahoo_scraper import get_yahoo_top_gainers
from modules.signal_analysis import generate_trade_signal
from modules.telegram_utils import send_telegram_alert

from datetime import datetime
import time

def run_yahoo_gainers_analysis():
    tickers = get_yahoo_top_gainers(count=10)
    signals = []

    for ticker in tickers:
        signal, log = generate_trade_signal(ticker)
        store_debug_log(log)
        if signal is not None:
            signals.append(signal)

    today = datetime.now().strftime("%d.%m.%Y")
    message = f"🚨 DTIA Yahoo Gainers Analyse für {today}\n\n"

    if not signals:
        message += "⚠️ Keine verwertbaren Signale gefunden."
    else:
        for sig in signals[:3]:
            message += (
                f"{sig['symbol']} {sig['direction']} @ {sig['entry']} → 🎯 {sig['target']} | "
                f"⛔ {sig['stop']} {sig['signal_strength']}\n"
            )

    send_telegram_alert(message)


# Am Ende der Datei dtia_trading_alerts.py einfügen

debug_logs_storage = []

def store_debug_log(entry):
    debug_logs_storage.append(entry)

def get_debug_logs():
    return debug_logs_storage
