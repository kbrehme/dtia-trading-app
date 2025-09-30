
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np

def calculate_gap(df):
    try:
        prev_close = df["Close"].iloc[-2]
        today_open = df["Open"].iloc[-1]
        return (today_open - prev_close) / prev_close
    except:
        return None

def calculate_rvol(df):
    try:
        avg_vol_10 = df["Volume"].tail(10).mean()
        today_vol = df["Volume"].iloc[-1]
        return today_vol / avg_vol_10 if avg_vol_10 > 0 else None
    except:
        return None

def calculate_volatility_percent(df):
    try:
        atr = (df["High"] - df["Low"]).rolling(window=3).mean().iloc[-1]
        price = df["Close"].iloc[-1]
        return atr / price if price > 0 else None
    except:
        return None

def passes_advanced_filters(df):
    """
    Input: df mit 30-Minuten- oder Tagesdaten
    Output: Tuple (True/False, [reasons])
    """
    reasons = []
    valid = True

    gap = calculate_gap(df)
    if gap is None or abs(gap) < 0.03:
        valid = False
        reasons.append("🔸 Gap < 3%")

    rvol = calculate_rvol(df)
    if rvol is None or rvol < 2.0:
        valid = False
        reasons.append("📊 RVOL < 2.0")

    price = df["Close"].iloc[-1]
    if price < 5 or price > 100:
        valid = False
        reasons.append("💰 Preis nicht im Range ($5-$100)")

    vol_perc = calculate_volatility_percent(df)
    if vol_perc is None or vol_perc < 0.015:
        valid = False
        reasons.append("📉 Volatilität zu gering (< 1.5%)")

    volume = df["Volume"].iloc[-1]
    if volume < 200000:
        valid = False
        reasons.append("📦 Volumen < 200k")

    return valid, reasons
