import yfinance as yf
import pandas as pd
import numpy as np

def generate_trade_signal(symbol):
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
        # 1️⃣ Daten abrufen – genug Historie für Indikatoren
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

        latest_rsi = rsi_series.iloc[-1] if not rsi_series.empty else None
        latest_rsi = float(latest_rsi) if pd.notna(latest_rsi) else None
        debug_log["rsi"] = round(latest_rsi, 2) if latest_rsi else None

        # 3️⃣ ATR berechnen
        df["H-L"] = df["High"] - df["Low"]
        df["H-PC"] = abs(df["High"] - df["Close"].shift(1))
        df["L-PC"] = abs(df["Low"] - df["Close"].shift(1))
        df["TR"] = df[["H-L", "H-PC", "L-PC"]].max(axis=1)

        atr_series = df["TR"].rolling(window=14).mean()
        atr = atr_series.iloc[-1] if not atr_series.empty else None
        atr = float(atr) if pd.notna(atr) else None
        debug_log["atr"] = round(atr, 2) if atr else None

        # 4️⃣ Volumen
        if "Volume" in df.columns and not df["Volume"].isna().all():
            volume = df["Volume"].iloc[-1]
            volume = int(volume) if pd.notna(volume) else None
        else:
            volume = None
        debug_log["volume"] = volume

        # 5️⃣ Gap berechnen
        if len(df) >= 2:
            prev_close = df["Close"].iloc[-2]
            today_open = df["Open"].iloc[-1]
            if pd.notna(prev_close) and pd.notna(today_open) and prev_close != 0:
                gap = (today_open - prev_close) / prev_close
                gap = float(gap)
            else:
                gap = None
        else:
            gap = None
        debug_log["gap"] = round(gap, 4) if isinstance(gap, float) else None

        # 6️⃣ Trend bestimmen
        df["EMA5"] = df["Close"].ewm(span=5, adjust=False).mean()
        df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
        ema5 = df["EMA5"].iloc[-1]
        ema20 = df["EMA20"].iloc[-1]
        trend = "Bullish" if ema5 > ema20 else "Bearish"
        debug_log["trend"] = trend

        # 7️⃣ Filterbedingungen robust prüfen
        is_valid_rsi = isinstance(latest_rsi, (float, int)) and 30 < latest_rsi < 70
        is_valid_atr = isinstance(atr, (float, int)) and atr > 0
        is_valid_volume = isinstance(volume, (float, int)) and volume > 100_000
        is_valid_gap = isinstance(gap, (float, int)) and abs(gap) < 0.05

        if all([is_valid_rsi, is_valid_atr, is_valid_volume, is_valid_gap]):
            debug_log["valid"] = True
            direction = "Long" if trend == "Bullish" else "Short"
            entry = float(df["Close"].iloc[-1])
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
