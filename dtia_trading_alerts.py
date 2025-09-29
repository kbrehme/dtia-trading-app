
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
    url = "https://finviz.com/screener.ashx?v=111&s=ta_topgainers&f=cap_largeover,sh_avgvol_o1000&ft=4"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'lxml')
    table = soup.find_all('table')[6]
    rows = table.find_all('tr')[1:]
    symbols = []
    for row in rows[:10]:
        cols = row.find_all('td')
        if cols:
            symbols.append(cols[1].text)
    return symbols[:3]

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
    message = f"🚨 DTIA Multi-Market Picks für {datetime.now().strftime('%d.%m.%Y')}\n"

    # US Stocks
    us_symbols = get_us_top_gainers()
    message += "\n🇺🇸 US Stocks\n"
    if not us_symbols:
        message += "❌ Es konnten keine Daten von Finviz gelesen werden.\n"
    else:
        us_signals = get_top_signals(us_symbols)
        if us_signals:
            for i, p in enumerate(us_signals, 1):
                message += f"{i}️⃣ {p['symbol']} – {p['direction']} {p['signal_strength']}\n"
                message += f"Entry: {p['entry']} | SL: {p['stop']} | TP: {p['target']}\n"
        else:
            message += "⚠️ Keine gute Aktie gefunden.\n"

    # DAX Stocks
    message += "\n🇩🇪 DAX Picks\n"
    if not DAX_SYMBOLS:
        message += "❌ Es konnten keine DAX-Daten gelesen werden.\n"
    else:
        dax_signals = get_top_signals(DAX_SYMBOLS)
        if dax_signals:
            for i, p in enumerate(dax_signals, 1):
                message += f"{i}️⃣ {p['symbol']} – {p['direction']} {p['signal_strength']}\n"
                message += f"Entry: {p['entry']} | SL: {p['stop']} | TP: {p['target']}\n"
        else:
            message += "⚠️ Keine gute Aktie gefunden.\n"

    # Krypto
    message += "\n₿ Crypto Picks\n"
    if not CRYPTO_SYMBOLS:
        message += "❌ Es konnten keine Kryptodaten gelesen werden.\n"
    else:
        crypto_signals = get_top_signals(CRYPTO_SYMBOLS)
        if crypto_signals:
            for i, p in enumerate(crypto_signals, 1):
                message += f"{i}️⃣ {p['symbol']} – {p['direction']} {p['signal_strength']}\n"
                message += f"Entry: {p['entry']} | SL: {p['stop']} | TP: {p['target']}\n"
        else:
            message += "⚠️ Keine gute Kryptowährung gefunden.\n"

    send_telegram_alert(message)


    # US Stocks
    us_symbols = get_us_top_gainers()
    if not us_symbols:
        message += "\n🇺🇸 US Stocks\n❌ Es konnten keine Daten von Finviz gelesen werden.\n"
    else:
        us_signals = get_top_signals(us_symbols)
        message += "\n🇺🇸 US Stocks\n"
        if us_signals:
            for i, p in enumerate(us_signals, 1):
                message += f"{i}️⃣ {p['symbol']} – {p['direction']} {p['signal_strength']}\n"
                message += f"Entry: {p['entry']} | SL: {p['stop']} | TP: {p['target']}\n"
        else:
            message += "⚠️ Keine gute Aktie gefunden.\n"

    # DAX Stocks
    message += "\n🇩🇪 DAX Picks\n"
    dax_signals = get_top_signals(DAX_SYMBOLS)
    if dax_signals:
        for i, p in enumerate(dax_signals, 1):
            message += f"{i}️⃣ {p['symbol']} – {p['direction']} {p['signal_strength']}\n"
            message += f"Entry: {p['entry']} | SL: {p['stop']} | TP: {p['target']}\n"
    else:
        message += "⚠️ Keine gute Aktie gefunden.\n"

    # Krypto
    message += "\n₿ Crypto Picks\n"
    crypto_signals = get_top_signals(CRYPTO_SYMBOLS)
    if crypto_signals:
        for i, p in enumerate(crypto_signals, 1):
            message += f"{i}️⃣ {p['symbol']} – {p['direction']} {p['signal_strength']}\n"
            message += f"Entry: {p['entry']} | SL: {p['stop']} | TP: {p['target']}\n"
    else:
        message += "⚠️ Keine gute Kryptowährung gefunden.\n"

    send_telegram_alert(message)


    us_symbols = get_us_top_gainers()
    us_signals = get_top_signals(us_symbols)
    message += "\n🇺🇸 US Stocks\n"
    for i, p in enumerate(us_signals, 1):
        message += f"{i}️⃣ {p['symbol']} – {p['direction']} {p['signal_strength']}\n"
        message += f"Entry: {p['entry']} | SL: {p['stop']} | TP: {p['target']}\n"

    dax_signals = get_top_signals(DAX_SYMBOLS)
    message += "\n🇩🇪 DAX Picks\n"
    for i, p in enumerate(dax_signals, 1):
        message += f"{i}️⃣ {p['symbol']} – {p['direction']} {p['signal_strength']}\n"
        message += f"Entry: {p['entry']} | SL: {p['stop']} | TP: {p['target']}\n"

    crypto_signals = get_top_signals(CRYPTO_SYMBOLS)
    message += "\n₿ Crypto Picks\n"
    for i, p in enumerate(crypto_signals, 1):
        message += f"{i}️⃣ {p['symbol']} – {p['direction']} {p['signal_strength']}\n"
        message += f"Entry: {p['entry']} | SL: {p['stop']} | TP: {p['target']}\n"

    send_telegram_alert(message)
