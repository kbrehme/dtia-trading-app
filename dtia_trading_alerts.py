
import requests
import yfinance as yf
from bs4 import BeautifulSoup
from datetime import datetime

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
        df = yf.download(symbol, period="5d", interval="1h")
        if df.empty:
            print(f"⚠️ Keine Daten für {symbol}")
            return None

        last_close = df['Close'].iloc[-1]
        last_open = df['Open'].iloc[-1]
        high = df['High'].max()
        low = df['Low'].min()
        atr = (high - low) / 10

        # Richtung basierend auf Wochenverlauf
        trend = df['Close'].iloc[-1] - df['Close'].iloc[0]
        direction = "Long" if trend > 0 else "Short"
        entry = round(last_close, 2)
        stop = round(entry - atr if direction == "Long" else entry + atr, 2)
        target = round(entry + 2 * atr if direction == "Long" else entry - 2 * atr, 2)

        # Signalbewertung
        signal_strength = "🔥🔥🔥" if abs(trend / last_close) > 0.03 else "⚠️"

        print(f"✅ Signal erzeugt für {symbol}: {direction}, Stärke {signal_strength}, Entry {entry}")
        return {
            "symbol": symbol,
            "direction": direction,
            "entry": entry,
            "stop": stop,
            "target": target,
            "signal_strength": signal_strength
        }

    except Exception as e:
        print(f"❌ Fehler bei Analyse von {symbol}: {e}")
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
