
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

    # Grundprüfungen
    if df.empty or len(df) < 5 or "Close" not in df.columns:
        debug_log["valid"] = False
        debug_log["reasons"].append("❌ Nicht genügend Daten oder Spalten fehlen")
        return debug_log

    try:
        df["returns"] = df["Close"].pct_change()
    except Exception as e:
        debug_log["valid"] = False
        debug_log["reasons"].append(f"⚠️ Fehler bei returns: {e}")
        return debug_log

    try:
        atr = (df["High"] - df["Low"]).rolling(window=3).mean().iloc[-1]
        avg_volume = df["Volume"].mean()
    except Exception as e:
        debug_log["valid"] = False
        debug_log["reasons"].append(f"⚠️ Fehler bei ATR oder Volumen: {e}")
        return debug_log

    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(window=6).mean()
    loss = -delta.clip(upper=0).rolling(window=6).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    try:
        last_rsi = float(rsi.iloc[-1])
    except:
        last_rsi = None

    # Ergebnisse speichern
    debug_log["rsi"] = round(last_rsi, 2) if last_rsi is not None else None
    debug_log["atr"] = round(atr, 2) if pd.notna(atr) else None
    debug_log["volume"] = int(avg_volume) if pd.notna(avg_volume) else None

    # Prüfen
    if pd.isna(avg_volume) or float(avg_volume) < 50000:
        debug_log["valid"] = False
        debug_log["reasons"].append("📉 Volumen zu niedrig oder ungültig (< 50k)")

    if pd.isna(atr) or atr < 0.5:
        debug_log["valid"] = False
        debug_log["reasons"].append("📏 ATR zu gering (< 0.5)")

    if atr > 10:
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
