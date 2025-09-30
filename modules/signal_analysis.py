
import yfinance as yf
from datetime import datetime, timedelta
from modules.advanced_filters import passes_advanced_filters



# Bewertungsskala:
# Jede positive Eigenschaft bringt +1 Punkt (max ca. 6)
# Interpretation in der UI:
#   5–6 Punkte = 🟢 Sehr stark
#   3–4 Punkte = 🟡 Solide
#   0–2 Punkte = 🔴 Schwach

# Scoring-System integriert

def generate_trade_signal(symbol):
    now = datetime.utcnow()
    start_date = (now - timedelta(days=2)).replace(hour=0, minute=0)
    end_date = now

    df = yf.download(symbol, start=start_date.strftime('%Y-%m-%d'),
                     end=end_date.strftime('%Y-%m-%d'), interval="30m", progress=False)

    log = {
        "symbol": symbol,
        "valid": True,
        "reasons": [],
        "rsi": None,
        "atr": None,
        "volume": None,
        "direction": None
    }

    if df.empty or len(df) < 5:
        log['reasons'].append(f"❌ Keine Kursdaten – erhaltene Zeilen: {len(df)}")
        log["valid"] = False
        log["reasons"].append("❌ Nicht genügend Daten")
        log['score'] = log.get('score', 0)
    return None, log

    passes_filters, filter_reasons = passes_advanced_filters(df)
    if not passes_filters:
        log["valid"] = False
        log["reasons"].extend(filter_reasons)
        log['score'] = log.get('score', 0)
    return None, log

    # RSI
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(window=6).mean()
    loss = -delta.clip(upper=0).rolling(window=6).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    last_rsi = rsi.iloc[-1] if not rsi.empty else None

    # ATR + Volume
    atr = (df["High"] - df["Low"]).rolling(window=3).mean().iloc[-1]
    avg_volume = df["Volume"].mean()
    price = df["Close"].iloc[-1]

    log["rsi"] = round(last_rsi, 2) if last_rsi is not None else None
    log["atr"] = round(atr, 2)
    log["volume"] = int(avg_volume)

    if avg_volume < 50000:
        log["valid"] = False
        log["reasons"].append("📉 Volumen < 50k")

    if atr < 0.5 or atr > 10:
        log["valid"] = False
        log["reasons"].append(f"📏 ATR ungültig ({atr:.2f})")

    if last_rsi is None:
        log["valid"] = False
        log["reasons"].append("🔸 RSI nicht berechenbar")
        log['score'] = log.get('score', 0)
    return None, log

    if last_rsi > 70:
        direction = "📉 Short"
    elif last_rsi < 30:
        direction = "📈 Long"
    else:
        log["valid"] = False
        log["reasons"].append("🔸 RSI neutral")
        log['score'] = log.get('score', 0)
    return None, log

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

    log["direction"] = direction
    return signal, log
