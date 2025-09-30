import os

BASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data')

def _load_tickers_from_file(filename: str, limit: int = 100):
    path = os.path.join(BASE_PATH, filename)
    try:
        with open(path, "r") as f:
            tickers = [line.strip() for line in f if line.strip()]
        return tickers[:limit]
    except FileNotFoundError:
        return []

def get_us_tickers(limit: int = 100):
    return _load_tickers_from_file("us_tickers.txt", limit)

def get_dax_tickers(limit: int = 100):
    return _load_tickers_from_file("dax_tickers.txt", limit)

def get_crypto_tickers(limit: int = 100):
    return _load_tickers_from_file("crypto_tickers.txt", limit)
