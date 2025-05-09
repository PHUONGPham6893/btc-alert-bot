import os
import requests
import telegram
import schedule
import time
from datetime import datetime, timedelta

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = telegram.Bot(token=BOT_TOKEN)

# Lưu lịch sử giá tạm thời trong RAM
history = {
    "bitcoin": {},
    "ethereum": {}
}

def get_price(symbol):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()
    return float(data[symbol]["usd"])

def save_price(symbol, price):
    today = datetime.now().date()
    history[symbol][today] = price

def get_history_price(symbol, days_ago):
    target_day = datetime.now().date() - timedelta(days=days_ago)
    return history[symbol].get(target_day, None)

def format_report(symbol, current, old_7d, old_30d):
    changes = []
    if old_7d is not None:
        diff = current - old_7d
        pct = (diff / old_7d) * 100
        changes.append(f"So với 7 ngày trước: {diff:.2f} USD ({pct:+.2f}%)")
    if old_30d is not None:
        diff = current - old_30d
        pct = (diff / old_30d) * 100
        changes.append(f"So với 30 ngày trước: {diff:.2f} USD ({pct:+.2f}%)")
    return f"- {symbol.upper()}: {current:.2f} USD\n  " + "\n  ".join(changes)

def send_alert():
    btc = get_price("bitcoin")
    eth = get_price("ethereum")

    save_price("bitcoin", btc)
    save_price("ethereum", eth)

    old_btc_7d = get_history_price("bitcoin", 7)
    old_btc_30d = get_history_price("bitcoin", 30)
    old_eth_7d = get_history_price("ethereum", 7)
    old_eth_30d = get_history_price("ethereum", 30)

    now = datetime.now().strftime("%H:%M %d/%m/%Y")
    msg = f"""[THÔNG BÁO GIÁ]
{format_report("bitcoin", btc, old_btc_7d, old_btc_30d)}
{format_report("ethereum", eth, old_eth_7d, old_eth_30d)}

Thời gian: {now}
"""

    bot.send_message(chat_id=CHAT_ID, text=msg)

# Lên lịch gửi lúc 08:00 và 20:00
schedule.every().day.at("08:00").do(send_alert)
schedule.every().day.at("20:00").do(send_alert)

# Vòng lặp chính
while True:
    schedule.run_pending()
    time.sleep(60)
