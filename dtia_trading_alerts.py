import requests
from bs4 import BeautifulSoup
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import warnings
import logging

# === KONFIGURATION ==
BOT_TOKEN = "7521010029:AAF87jAzPWf0Kjz9hdymPKnVbRamCVGmhZQ"
CHAT_ID = "6501591390"
TOP_N = 10  # Anzahl Gainer, die von Yahoo gescannt werden

warnings.simplefilter(action='ignore', category=FutureWarning)



# === LOGGING ===
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# === 1. Scrape Top Gainers von Yahoo Finance ===
def get_yahoo_top_gainers(count=10):
    logging.info("🔍 Hole Top Gainers von Yahoo Finance...")
    url = "https://finance.yahoo.com/gainers"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "lxml")

    tickers = []
    rows = soup.select("table tbody tr")
    for row in rows[:count]:
        symbol_cell = row.find("td")
        if symbol_cell:
            ticker = symbol_cell.text.strip()
            tickers.append(ticker)

    logging.info(f"✅ Gefundene Top Ticker: {tickers}")
    return tickers

# === 2. Analyse: RSI, ATR, Richtung ===
def generate_trade_signal(symbol):
    try:
        logging.info(f"📊 Analysiere: {symbol}")
        now = datetime.utcnow()
        start_date = (now - timedelta(days=2)).replace(hour=0, minute=0)
        end_date = now

        df = yf.download(symbol, start=start_date.strftime('%Y-%m-%d'),
                         end=end_date.strftime('%Y-%m-%d'), interval="30m", progress=False)

        if df.empty or len(df) < 5:
            logging.warning(f"⚠️ Keine oder ungenügende Daten für {symbol}")
            return None

        df["returns"] = df["Close"].pct_change()
        atr = (df["High"] - df["Low"]).rolling(window=3).mean().iloc[-1]
        avg_volume = df["Volume"].mean()

        delta = df["Close"].diff()
        gain = delta.clip(lower=0).rolling(window=6).mean()
        loss = -delta.clip(upper=0).rolling(window=6).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        last_rsi = rsi.iloc[-1]

        if avg_volume < 50000 or atr < 0.5 or atr > 10:
            return None

        if last_rsi > 70:
            direction = "Short"
        elif last_rsi < 30:
            direction = "Long"
        else:
            return None

        entry = round(df["Close"].iloc[-1], 2)
        stop = round(entry - atr if direction == "Long" else entry + atr, 2)
        target = round(entry + 2 * atr if direction == "Long" else entry - 2 * atr, 2)
        signal_strength = "🔥🔥🔥" if abs(df["returns"].sum()) > 0.03 else "⚠️"

        return {
            "symbol": symbol,
            "direction": direction,
            "entry": entry,
            "stop": stop,
            "target": target,
            "signal_strength": signal_strength
        }
    except Exception as e:
        logging.error(f"❌ Fehler bei {symbol}: {e}")
        return None

# === 3. Telegram senden ===
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload)
        logging.info("📤 Telegram Nachricht gesendet.")
    except Exception as e:
        logging.error(f"❌ Telegram Fehler: {e}")

# === 4. Strategie ausführen ===
def run_yahoo_gainers_analysis():
    tickers = get_yahoo_top_gainers(TOP_N)
    signals = []

    for ticker in tickers:
        signal = generate_trade_signal(ticker)
        if signal:
            signals.append(signal)
        time.sleep(1)  # Anti-Rate-Limit

    today = datetime.now().strftime("%d.%m.%Y")
    message = f"🚨 DTIA Yahoo Gainers Analyse für {today}\n\n"

    if not signals:
        message += "⚠️ Keine verwertbaren Signale gefunden."
    else:
        for sig in signals[:3]:  # nur Top 3 senden
            message += (
                f"{sig['symbol']} {sig['direction']} @ {sig['entry']} → 🎯 {sig['target']} | "
                f"⛔ {sig['stop']} {sig['signal_strength']}\n"
            )

    send_telegram_alert(message)

# === Entry Point ===
if __name__ == "__main__":
    run_yahoo_gainers_analysis()


    # Rückgabe für Streamlit-Chart
    return all_signals
