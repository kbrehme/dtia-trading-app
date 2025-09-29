
import requests
import yfinance as yf
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

BOT_TOKEN = "7521010029:AAF87jAzPWf0Kjz9hdymPKnVbRamCVGmhZQ"
CHAT_ID = "6501591390"

def send_telegram_alert(message):
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    payload = {'chat_id': CHAT_ID, 'text': message}
    requests.post(url, data=payload)

def get_us_top_gainers():
    try:
        url = "https://finviz.com/screener.ashx?v=111&s=ta_topgainers&f=cap_largeover,sh_avgvol_o1000&ft=4"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'lxml')

        tables = soup.find_all('table')
        if len(tables) < 7:
            print("❌ Tabelle nicht gefunden.")
            return []

        table = tables[6]
        rows = table.find_all('tr')[1:]  # Erste Zeile = Header
        symbols = []

        for row in rows[:10]:  # Nur Top 10 prüfen
            cols = row.find_all('td')
            if len(cols) > 1:
                symbols.append(cols[1].text.strip())

        return symbols[:3] if symbols else []
    
    except Exception as e:
        print(f"❌ Fehler beim Abrufen der US-Gainer: {e}")
        return []

DAX_SYMBOLS = ["SAP.DE", "DTE.DE", "ALV.DE", "BMW.DE", "BAYN.DE", "VOW3.DE"]
CRYPTO_SYMBOLS = ["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "ADA-USD"]

def generate_trade_signal(symbol):
    try:
        df = yf.download(symbol, period="5d", interval="1h")
        if df.empty:
            return None
        last_close = df['Close'].iloc[-1]
        high = df['High'].max()
        low = df['Low'].min()
        atr = (high - low) / 10
        direction = "Long" if df['Close'].iloc[-1] > df['Open'].iloc[-1] else "Short"
        entry = round(last_close, 2)
        stop = round(entry - atr if direction == "Long" else entry + atr, 2)
        target = round(entry + 2 * atr if direction == "Long" else entry - 2 * atr, 2)
        return {
            "symbol": symbol,
            "direction": direction,
            "entry": entry,
            "stop": stop,
            "target": target,
            "signal_strength": "🔥🔥🔥"
        }
    except:
        return None

def get_top_signals(symbols):
    signals = []
    for sym in symbols:
        sig = generate_trade_signal(sym)
        if sig:
            signals.append(sig)
        if len(signals) == 3:
            break
    return signals



def run_full_strategy():
    sections = []  # Für saubere Nachricht zusammensetzung
    header = f"🚨 DTIA Multi-Market Picks für {datetime.now().strftime('%d.%m.%Y')}\n"

    # US Stocks
    us_block = "🇺🇸 US Stocks\n"
    us_symbols = get_us_top_gainers()
    if not us_symbols:
        us_block += "❌ Es konnten keine Daten von Finviz gelesen werden.\n"
    else:
        us_signals = get_top_signals(us_symbols)
        if us_signals:
            for i, p in enumerate(us_signals, 1):
                us_block += f"{i}️⃣ {p['symbol']} – {p['direction']} {p['signal_strength']}\n"
                us_block += f"Entry: {p['entry']} | SL: {p['stop']} | TP: {p['target']}\n"
        else:
            us_block += "⚠️ Keine gute Aktie gefunden.\n"
    sections.append(us_block)

    # DAX Stocks
    dax_block = "🇩🇪 DAX Picks\n"
    dax_signals = get_top_signals(DAX_SYMBOLS)
    if dax_signals:
        for i, p in enumerate(dax_signals, 1):
            dax_block += f"{i}️⃣ {p['symbol']} – {p['direction']} {p['signal_strength']}\n"
            dax_block += f"Entry: {p['entry']} | SL: {p['stop']} | TP: {p['target']}\n"
    else:
        dax_block += "⚠️ Keine gute Aktie gefunden.\n"
    sections.append(dax_block)

    # Krypto
    crypto_block = "₿ Crypto Picks\n"
    crypto_signals = get_top_signals(CRYPTO_SYMBOLS)
    if crypto_signals:
        for i, p in enumerate(crypto_signals, 1):
            crypto_block += f"{i}️⃣ {p['symbol']} – {p['direction']} {p['signal_strength']}\n"
            crypto_block += f"Entry: {p['entry']} | SL: {p['stop']} | TP: {p['target']}\n"
    else:
        crypto_block += "⚠️ Keine gute Kryptowährung gefunden.\n"
    sections.append(crypto_block)

    # Nachricht zusammenbauen
    full_message = header + "\n".join(sections)
    send_telegram_alert(full_message)
