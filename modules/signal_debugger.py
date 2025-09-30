
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

def debug_trade_signal(symbol):
    now = datetime.utcnow()
    start_date = (now - timedelta(days=2)).replace(hour=0, minute=0)
    end_date = now

    df = yf.download(symbol, start=start_date.strftime('%Y-%m-%d'),
                     end=end_date.strftime('%Y-%m-%d'), interval="30m", progress=False)

    debug_log = {
        "symbol": symbol,
        "valid": True,
        "reasons": [],
        "rsi": None,
        "atr": None,
        "volume": None
    }

    if df.empty or len(df) < 5:
        debug_log["valid"] = False
        debug_log["reasons"].append("❌ Kein ausreichender Datenbestand")
        return debug_log

    df["returns"] = df["Close"].pct_change()
    atr = (df["High"] - df["Low"]).rolling(window=3).mean().iloc[-1]
    avg_volume = df["Volume"].mean()

    # Werte validieren
    try:
        avg_volume_val = float(avg_volume)
    except:
        avg_volume_val = None

    try:
        atr_val = float(atr)
    except:
        atr_val = None

    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(window=6).mean()
    loss = -delta.clip(upper=0).rolling(window=6).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    try:
        last_rsi = float(rsi.iloc[-1])
    except:
        last_rsi = None

    debug_log["rsi"] = round(last_rsi, 2) if last_rsi is not None else None
    debug_log["atr"] = round(atr_val, 2) if atr_val is not None else None
    debug_log["volume"] = int(avg_volume_val) if avg_volume_val is not None else None

    # Kriterien prüfen
    if avg_volume_val is None or avg_volume_val < 50000:
        debug_log["valid"] = False
        debug_log["reasons"].append("📉 Volumen zu niedrig oder ungültig (< 50k)")

    if atr_val is None or atr_val < 0.5:
        debug_log["valid"] = False
        debug_log["reasons"].append("📏 ATR zu gering (< 0.5)")

    if atr_val is not None and atr_val > 10:
        debug_log["valid"] = False
        debug_log["reasons"].append("📏 ATR zu hoch (> 10)")

    if last_rsi is None:
        debug_log["valid"] = False
        debug_log["reasons"].append("🔸 RSI nicht berechenbar")
    elif last_rsi > 70:
        debug_log["signal"] = "Short"
    elif last_rsi < 30:
        debug_log["signal"] = "Long"
    else:
        debug_log["valid"] = False
        debug_log["reasons"].append("🔸 RSI neutral (zwischen 30 und 70)")

    return debug_log

def debug_multiple_tickers(tickers):
    results = []
    for symbol in tickers:
        result = debug_trade_signal(symbol)
        results.append(result)
    return results
