from flask import Flask, render_template, request
import yfinance as yf
import pandas as pd
import numpy as np

app = Flask(__name__)

def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

@app.route("/", methods=["GET", "POST"])
def home():
    signal = None

    if request.method == "POST":
        stock = request.form["stock"]

        data = yf.download(stock, start="2022-01-01")

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)

        data['MA_50'] = data['Close'].rolling(50).mean()
        data['MA_200'] = data['Close'].rolling(200).mean()
        data['RSI'] = calculate_rsi(data)

        data = data.dropna()

        last = data.iloc[-1]

        if last['MA_50'] > last['MA_200'] and last['RSI'] < 70:
            signal = "BUY"
        elif last['MA_50'] < last['MA_200'] and last['RSI'] > 30:
            signal = "SELL"
        else:
            signal = "HOLD"

    return render_template("index.html", signal=signal)

if __name__ == "__main__":
    app.run(debug=False)