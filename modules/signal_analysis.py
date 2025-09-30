import yfinance as yf
import pandas as pd
import numpy as np

def generate_trade_signal(symbol):
    def safe_float(val):
        try:
            return float(val)
        except:
            return None

    debug_log = {
        "symbol": symbol,
        "valid": False,
        "score": None,
        "signal_strength": None,
        "rsi": None,
        "atr": None,
        "volume": None,
        "gap": None,
        "trend": None,
        "data_rows": 0,
        "reasons": []
    }

    try:
        # 1️⃣ Kursdaten abrufen
        df = yf.download(symbol, period="30d", interval="1d", progress=False)

        if df is None or df.empty or len(df) < 15:
            debug_log["reasons"].append("❌ Keine oder zu wenig Kursdaten")
            return None, debug_log

        debug_log["data_rows"] = len(df)

        # 2️⃣ RSI berechnen
        delta = df["Close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        rsi_series = 100 - (100 / (1 + rs))
        latest_rsi = safe_float(rsi_series.iloc[-1]) if not rsi_series.empty else None
        debug_log["rsi"] = round(latest_rsi, 2) if latest_rsi is not None else None

        # 3️⃣ ATR berechnen
        df["H-L"] = df["High"] - df["Low"]
        df["H-PC"] = abs(df["High"] - df["Close"].shift(1))
        df["L-PC"] = abs(df["Low"] - df["Close"].shift(1))
        df["TR"] = df[["H-L", "H-PC", "L-PC"]].max(axis=1)
        atr_series = df["TR"].rolling(window=14).mean()
        atr = safe_float(atr_series.iloc[-1]) if not atr_series.empty else None
        debug_log["atr"] = round(atr, 2) if atr is not None else None

        # 4️⃣ Volumen
        volume = safe_float(df["Volume"].iloc[-1]) if "Volume" in df.columns and not df["Volume"].isna().all() else None
        debug_log["volume"] = int(volume) if volume is not None else None

        # 5️⃣ Gap
        if len(df) >= 2:
            prev_close = safe_float(df["Close"].iloc[-2])
            today_open = safe_float(df["Open"].iloc[-1])
            if prev_close and today_open and prev_close != 0:
                gap = safe_float((today_open - prev_close) / prev_close)
            else:
                gap = None
        else:
            gap = None
        debug_log["gap"] = round(gap, 4) if gap is not None else None

        # 6️⃣ Trend (mit Fix!)
        df["EMA5"] = df["Close"].ewm(span=5, adjust=False).mean()
        df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
        ema5 = safe_float(df["EMA5"].iloc[-1])
        ema20 = safe_float(df["EMA20"].iloc[-1])

        if isinstance(ema5, (float, int)) and isinstance(ema20, (float, int)):
            trend = "Bullish" if ema5 > ema20 else "Bearish"
        else:
            trend = None

        debug_log["trend"] = trend

        if trend is None:
            debug_log["reasons"].append("❌ Trend nicht berechenbar")
            return None, debug_log

        # 7️⃣ Filterkriterien
        is_valid_rsi = latest_rsi is not None and 30 < latest_rsi < 70
        is_valid_atr = atr is not None and atr > 0
        is_valid_volume = volume is not None and volume > 100_000
        is_valid_gap = gap is not None and abs(gap) < 0.05

        if all([is_valid_rsi, is_valid_atr, is_valid_volume, is_valid_gap]):
            debug_log["valid"] = True
            direction = "Long" if trend == "Bullish" else "Short"
            entry = safe_float(df["Close"].iloc[-1])
            stop = entry - atr if direction == "Long" else entry + atr
            target = entry + 2 * atr if direction == "Long" else entry - 2 * atr
            signal_strength = "🟢 Stark"

            signal = {
                "symbol": symbol,
                "entry": round(entry, 2),
                "stop": round(stop, 2),
                "target": round(target, 2),
                "direction": direction,
                "score": 100,
                "signal_strength": signal_strength
            }

            return signal, debug_log

        else:
            debug_log["reasons"].append("❌ Bedingungen nicht erfüllt")
            return None, debug_log

    except Exception as e:
        debug_log["reasons"].append(f"❌ Fehler: {str(e)}")
        return None, debug_log
