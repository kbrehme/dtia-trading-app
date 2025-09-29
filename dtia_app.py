from flask import Flask, request
from dtia_trading_alerts import run_full_strategy

app = Flask(__name__)

@app.route("/run", methods=["GET"])
def run_strategy():
    try:
        run_full_strategy()
        return "✅ Strategie wurde erfolgreich ausgeführt.", 200
    except Exception as e:
        return f"❌ Fehler: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
