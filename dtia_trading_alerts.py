
import datetime
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import requests

BOT_TOKEN = "7521010029:AAF87jAzPWf0Kjz9hdymPKnVbRamCVGmhZQ"
CHAT_ID = "6501591390"


def get_top_gainers_from_yahoo(url, suffix_filter=None):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')

        table = soup.find('table', attrs={'class': 'W(100%)'})
        if not table:
            print(f"❌ Tabelle nicht gefunden auf {url}")
            return []

        rows = table.find_all('tr')[1:]
        symbols = []

        for row in rows[:10]:
            cols = row.find_all('td')
            if len(cols) > 0:
                symbol = cols[0].text.strip()
                if suffix_filter is None or symbol.endswith(suffix_filter):
                    symbols.append(symbol)

        print(f"✅ Gefundene Symbole ({url}): {symbols}")
        return symbols[:5] if symbols else []
    except Exception as e:
        print(f"❌ Fehler beim Scraping ({url}): {e}")
        return []


def generate_trade_signal(symbol):
    try:
        print(f"📊 Analysiere: {symbol}")
        
        # Zeitraum: Gestern + Heute
        now = datetime.datetime.utcnow()
        start_date = (now - datetime.timedelta(days=2)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now

        df = yf.download(symbol, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), interval="30m")

        if df.empty or len(df) < 5:
            print(f"⚠️ Nicht genug Daten für {symbol}")
            return None

        # Strukturindikatoren auf Vortag
        df_yesterday = df[df.index.date == (now - datetime.timedelta(days=1)).date()]
        if df_yesterday.empty:
            print(f"📉 Keine Daten vom Vortag für {symbol}")
            return None

        avg_volume_yesterday = df_yesterday["Volume"].mean()
        atr_yesterday = (df_yesterday["High"] - df_yesterday["Low"]).rolling(window=3).mean().iloc[-1]

        # Entry-Indikatoren auf heutigen Tag
        df_today = df[df.index.date == now.date()]
        if df_today.empty or len(df_today) < 2:
            print(f"📉 Keine aktuellen Daten für {symbol}")
            return None

        delta = df_today["Close"].diff()
        gain = delta.clip(lower=0).rolling(window=6).mean()
        loss = -delta.clip(upper=0).rolling(window=6).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        last_rsi = rsi.iloc[-1]

        # Entscheidung basierend auf RSI
        if last_rsi > 70:
            direction = "Short"
        elif last_rsi < 30:
            direction = "Long"
        else:
            print(f"⚖️ RSI neutral ({last_rsi:.1f}) für {symbol}")
            return None

        # Entry/Exit-Berechnung
        entry = round(df_today["Close"].iloc[-1], 2)
        stop = round(entry - atr_yesterday if direction == "Long" else entry + atr_yesterday, 2)
        target = round(entry + 2 * atr_yesterday if direction == "Long" else entry - 2 * atr_yesterday, 2)

        signal_strength = "🔥🔥🔥" if abs(df_today["Close"].pct_change().sum()) > 0.02 else "⚠️"

        print(f"✅ Signal: {symbol} ({direction}) RSI {last_rsi:.1f} ATR {atr_yesterday:.2f}")

        return {
            "symbol": symbol,
            "direction": direction,
            "entry": entry,
            "stop": stop,
            "target": target,
            "signal_strength": signal_strength
        }

    except Exception as e:
        print(f"❌ Fehler bei {symbol}: {e}")
        return None


def analyze_and_format_signals(name, symbols):
    message_block = f"\n{name}\n"
    if not symbols:
        message_block += "❌ Es konnten keine Daten geladen werden.\n"
        return message_block

    signals = []
    for sym in symbols:
        sig = generate_trade_signal(sym)
        if sig:
            signals.append(sig)
        if len(signals) == 3:
            break

    if signals:
        for i, p in enumerate(signals, 1):
            message_block += f"{i}️⃣ {p['symbol']} – {p['direction']} {p['signal_strength']}\n"
            message_block += f"Entry: {p['entry']} | SL: {p['stop']} | TP: {p['target']}\n"
    else:
        message_block += "⚠️ Keine guten Signale gefunden.\n"

    return message_block


def send_telegram_alert(message):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {'chat_id': CHAT_ID, 'text': message}
    requests.post(url, data=payload)


def run_full_strategy():
    message = f"🚨 DTIA Multi-Market Picks für {datetime.now().strftime('%d.%m.%Y')}\n"

    us_symbols = get_top_gainers_from_yahoo("https://finance.yahoo.com/gainers")
    dax_symbols = get_top_gainers_from_yahoo("https://de.finance.yahoo.com/gainers?e=XETRA", suffix_filter=".DE")
    crypto_symbols = get_top_gainers_from_yahoo("https://finance.yahoo.com/cryptocurrencies", suffix_filter="-USD")

    message += analyze_and_format_signals("🇺🇸 US Stocks", us_symbols)
    message += analyze_and_format_signals("🇩🇪 DAX Picks", dax_symbols)
    message += analyze_and_format_signals("₿ Crypto Picks", crypto_symbols)

    send_telegram_alert(message)
