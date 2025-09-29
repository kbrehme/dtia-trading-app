
import requests
from bs4 import BeautifulSoup

def get_yahoo_top_gainers(count=10):
    url = "https://finance.yahoo.com/gainers"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "lxml")

    tickers = []
    rows = soup.select("table tbody tr")
    for row in rows[:count]:
        symbol_cell = row.find("td")
        if symbol_cell:
            tickers.append(symbol_cell.text.strip())

    return tickers
