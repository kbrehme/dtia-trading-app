
import yfinance as yf
from datetime import datetime, timedelta
from modules.advanced_filters import passes_advanced_filters

def generate_trade_signal(symbol):
    now = datetime.utcnow()
    start_date = (now - timedelta(days=2)).replace(hour=0, minute=0)
    end_date = now

    df = yf.download(symbol, start=start_date.strftime('%Y-%m-%d'),
                     end=end_date.strftime('%Y-%m-%d'), interval="30m", progress=False)

    if df.empty or len(df) < 5:
        return None

    # Erweiterte Daytrader-Filter prüfen
    passes_filters, filter_reasons = passes_advanced_filters(df)
    if not passes_filters:
        return None  # Optional: filter_reasons in Debug-Modul zurückgeben

    # Technische Analyse: RSI
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(window=6).mean()
    loss = -delta.clip(upper=0).rolling(window=6).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    last_rsi = rsi.iloc[-1] if not rsi.empty else None

    if last_rsi is None:
        return None

    # Technische Analyse: ATR
    atr = (df["High"] - df["Low"]).rolling(window=3).mean().iloc[-1]
    avg_volume = df["Volume"].mean()
    price = df["Close"].iloc[-1]

    # Validierung technischer Kriterien
    if avg_volume < 50000 or atr < 0.5 or atr > 10:
        return None

    if last_rsi > 70:
        direction = "📉 Short"
    elif last_rsi < 30:
        direction = "📈 Long"
    else:
        return None

    signal = {
        "symbol": symbol,
        "rsi": round(last_rsi, 2),
        "atr": round(atr, 2),
        "volume": int(avg_volume),
        "price": round(price, 2),
        "direction": direction,
        "entry": round(price, 2),
        "target": round(price * 1.03 if direction == "📈 Long" else price * 0.97, 2),
        "stop": round(price * 0.98 if direction == "📈 Long" else price * 1.02, 2),
        "signal_strength": "🔥"
    }

    return signal
