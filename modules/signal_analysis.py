
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_trade_signal(symbol):
    try:
        now = datetime.utcnow()
        start_date = (now - timedelta(days=2)).replace(hour=0, minute=0)
        end_date = now

        df = yf.download(symbol, start=start_date.strftime('%Y-%m-%d'),
                         end=end_date.strftime('%Y-%m-%d'), interval="30m", progress=False)

        if df.empty or len(df) < 5:
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
    except:
        return None
