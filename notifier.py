import os
import time
import json
import threading
import datetime as dt
import requests

# Load configuration
with open('config.json') as f:
    config = json.load(f)

stock_symbols = config['symbols']
api_key = config['api_key']
notification_sound = 'true' if config.get('notification_sound', True) else 'false'

# Helper to send notification
def show_notification(title, content):
    os.system(
        f'termux-notification --title "{title}" --content "{content}" --sound {notification_sound} --vibrate 100'
    )

# Show selection menu
def show_menu():
    print("📊 Choose a stock to track:")
    for i, symbol in enumerate(stock_symbols):
        print(f"{i+1}. {symbol}")
    selection = int(input("\nEnter your choice (1-{}): ".format(len(stock_symbols))))
    return stock_symbols[selection - 1]

# Fetch stock price
def fetch_price(symbol):
    url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={api_key}"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception("API Error")
    data = response.json()
    return float(data['price'])

# Main function
def main():
    os.system('termux-wake-lock')  # prevent sleep

    stock = show_menu()
    initial_price = fetch_price(stock)
    last_jump_direction = None

    def update_loop():
        nonlocal last_jump_direction
        while True:
            try:
                current_price = fetch_price(stock)
                now = dt.datetime.now().strftime("%H:%M:%S")

                # Price popup
                title = f"[{stock}] ${current_price:.2f}"
                content = f"Updated: {now}"
                show_notification(title, content)

                # Trend detection
                if current_price > initial_price:
                    show_notification("📈 Uptrend", "Price is rising")
                elif current_price < initial_price:
                    show_notification("📉 Downtrend", "Price is falling")

                # Big jump alert
                change_pct = (current_price - initial_price) / initial_price * 100
                direction = "up" if change_pct > 0 else "down"
                if abs(change_pct) >= 2 and direction != last_jump_direction:
                    jump_title = (
                        f"🚀 Surge! [{stock}] +{change_pct:.2f}%"
                        if direction == "up"
                        else f"📉 Crash! [{stock}] {change_pct:.2f}%"
                    )
                    show_notification(jump_title, "Big move detected!")
                    last_jump_direction = direction

            except Exception as e:
                print("⚠️ Error:", e)

            time.sleep(5)

    # Start loop in background thread
    thread = threading.Thread(target=update_loop)
    thread.start()

    try:
        thread.join()
    except KeyboardInterrupt:
        print("\nExiting...")
        os.system('termux-wake-unlock')

if __name__ == "__main__":
    main()

