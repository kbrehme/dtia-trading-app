import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_trade_signal(symbol):
    debug_log = {
        "symbol": symbol,
        "valid": False,
        "reasons": [],
        "rsi": None,
        "atr": None,
        "volume": None,
        "gap": None,
        "trend": None,
        "data_rows": 0
    }

    try:
        # 1. 📥 Daten abrufen (letzte 10 Tage für solide Indikatoren)
        df = yf.download(symbol, period="10d", interval="1d", progress=False)

        if df is None or df.empty or len(df) < 5:
            debug_log["reasons"].append("❌ Keine oder zu wenig Kursdaten")
            return None, debug_log

        debug_log["data_rows"] = len(df)

        # 2. 📉 RSI (14)
        delta = df["Close"].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        latest_rsi = rsi.iloc[-1] if not rsi.empty else None
        debug_log["rsi"] = round(latest_rsi, 2) if pd.notna(latest_rsi) else None

        # 3. 📊 ATR (14)
        df["H-L"] = df["High"] - df["Low"]
        df["H-PC"] = abs(df["High"] - df["Close"].shift(1))
        df["L-PC"] = abs(df["Low"] - df["Close"].shift(1))
        df["TR"] = df[["H-L", "H-PC", "L-PC"]].max(axis=1)
        atr = df["TR"].rolling(window=14).mean().iloc[-1]
        debug_log["atr"] = round(atr, 2) if pd.notna(atr) else None

        # 4. 📦 Volumen
        volume = df["Volume"].iloc[-1] if "Volume" in df and not df["Volume"].isna().all() else None
        debug_log["volume"] = int(volume) if pd.notna(volume) else None

        # 5. 🧠 Gap (letzter Tag vs. Vortag Close)
        if len(df) >= 2:
            prev_close = df["Close"].iloc[-2]
            open_price = df["Open"].iloc[-1]
            gap = (open_price - prev_close) / prev_close
            debug_log["gap"] = round(gap, 4)
        else:
            gap = None
            debug_log["reasons"].append("❌ Kein vorheriger Close für Gap")

        # 6. 📈 Trend (EMA 5 vs EMA 20)
        df["EMA5"] = df["Close"].ewm(span=5, adjust=False).mean()
        df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()

        ema5 = df["EMA5"].iloc[-1]
        ema20 = df["EMA20"].iloc[-1]
        trend = "Bullish" if ema5 > ema20 else "Bearish"
        debug_log["trend"] = trend

        # 7. ✅ Signalbedingungen
        conditions = [
            pd.notna(latest_rsi) and 30 < latest_rsi < 70,
            pd.notna(atr) and atr > 0,
            pd.notna(volume) and volume > 100000,
            gap is not None and abs(gap) < 0.05
        ]

        if all(conditions):
            debug_log["valid"] = True
            direction = "Long" if trend == "Bullish" else "Short"
            entry = df["Close"].iloc[-1]
            stop = entry - atr if direction == "Long" else entry + atr
            target = entry + 2 * atr if direction == "Long" else entry - 2 * atr

            signal = {
                "symbol": symbol,
                "entry": round(entry, 2),
                "stop": round(stop, 2),
                "target": round(target, 2),
                "direction": direction,
                "score": 100,
                "signal_strength": "🟢 Stark"
            }
            return signal, debug_log

        else:
            debug_log["reasons"].append("❌ Bedingungen nicht erfüllt")
            return None, debug_log

    except Exception as e:
        debug_log["reasons"].append(f"❌ Fehler: {str(e)}")
        return None, debug_log
