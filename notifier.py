iimport requests
import os
import json
import time

API_KEY = "YOUR_API_KEY"  # Replace this with your actual Twelve Data API key
CHECK_INTERVAL = 5 * 60   # 5 minutes in seconds

def notify(title, message):
    os.system(f'termux-notification --title "{title}" --content "{message}"')

def get_price(symbol):
    url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        return float(data["price"])
    except Exception as e:
        print(f"Error getting price for {symbol}: {e}")
        return None

def load_config():
    with open("config.json") as f:
        return json.load(f)

def track_stocks():
    config = load_config()
    last_prices = {}

    while True:
        print("\n=== Stock Price Update ===")
        for symbol, settings in config.items():
            target = settings["target"]
            price = get_price(symbol)
            if price is None:
                continue

            message = f"{symbol}: ${price:.2f} (Target: ${target})"
            print(message)

            # Send update every time
            notify(f"Stock Update", message)

            # Notify if target is hit
            if price >= target:
                notify(f"{symbol} Target Hit", f"Price is ${price:.2f} (≥ ${target})")

            # Store the last price (can be used later to compare changes)
            last_prices[symbol] = price

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    track_stocks()

