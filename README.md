# 📈 Tradingkid – Yahoo Gainers Analyse

Dieses Projekt ist ein modular aufgebauter **Daytrading-Assistent**, der automatisch täglich die **Top-Gewinner (Gainers)** auf [Yahoo Finance](https://finance.yahoo.com/gainers) analysiert, technische Signale berechnet (RSI, ATR, Volumen etc.), und die besten Einstiegssignale per **Telegram** versendet.

---

## 📁 Projektstruktur

```
dtia-trading-app/
│
├── data/
│   ├── us_tickers.txt
│   ├── dax_tickers.txt
│   └── crypto_tickers.txt
│
├── modules/
│   ├── signal_analysis.py
│   ├── ticker_loader.py
│   └── ...
│
├── dtia_trading_alerts.py
├── dtia_app.py
└── ...
```

---

## 🚀 Start der Web-App (lokal)

```bash
streamlit run dtia_app.py
```

Alternativ kannst du die App auch über Streamlit Cloud deployen.

---

## 🔌 Automatischer Start per URL

Du kannst die Analyse auch automatisch beim Laden starten lassen:

```
http://localhost:8501/?run=true
```
oder online:
```
https://dein-app-name.streamlit.app/?run=true
```

---

## 📦 Abhängigkeiten

Installiere alle benötigten Pakete per:

```bash
pip install -r requirements.txt
```

---

## 💬 Telegram Konfiguration

1. Bot erstellen: https://t.me/BotFather
2. `TELEGRAM_TOKEN` und `TELEGRAM_CHAT_ID` in `modules/telegram_utils.py` eintragen.

---

## 🧩 Neue Funktionen einbinden

Wenn du neue Features (z. B. Charts, weitere Scanner, Backtests) einfügen willst, gehe wie folgt vor:

### Beispiel: Neue Funktion hinzufügen
1. Lege Datei an unter `modules/dein_modulname.py`
2. Implementiere deine Funktion z. B. `generate_chart()`
3. Importiere sie in `dtia_trading_alerts.py` oder `dtia_app.py`:
```python
from modules.dein_modulname import generate_chart
```
4. Verwende sie an gewünschter Stelle

---

## 🛠 Beispielmodul erstellen

```bash
touch modules/pre_market_analyzer.py
```

```python
# Inhalt der Datei:
def analyze_pre_market(symbol):
    # Logik hier einfügen
    pass
```

Dann in der Hauptdatei einfügen:

```python
from modules.pre_market_analyzer import analyze_pre_market
```

---

## ❓ Support

Für Erweiterungen, Debugging oder Trading-Strategien, wende dich an deinen DTIA-Assistenten im Chat 😉

---
