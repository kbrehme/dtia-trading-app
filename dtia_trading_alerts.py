from modules.signal_debugger import debug_multiple_tickers
from modules.yahoo_scraper import get_yahoo_top_gainers
from modules.signal_analysis import generate_trade_signal
from modules.telegram_utils import send_telegram_alert

from datetime import datetime
import time

def run_yahoo_gainers_analysis():
    tickers = get_yahoo_top_gainers(count=10)
    debug_logs = debug_multiple_tickers(tickers)
    signals = []

    for ticker in tickers:
        signal = generate_trade_signal(ticker)
        if signal:
            signals.append(signal)
        time.sleep(1)

    
for log in debug_logs:
    print(f"{log['symbol']}: ✅" if log['valid'] else f"{log['symbol']}: ❌ {' | '.join(log['reasons'])}")

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
