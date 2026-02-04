import os
import telebot
import pandas as pd
from datetime import datetime
from mytoken import TelegramConfig

bot = telebot.TeleBot(TelegramConfig().get_token())

CSV_FILE = "user_data.csv"
COLUMNS = ["user_id", "first_name", "last_name", "username", "message", "time"]


def append_to_csv_unique(row: dict):
    # If file exists, read it
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
    else:
        df = pd.DataFrame(columns=COLUMNS)

    # 🔒 Check duplicate user_id
    if row["user_id"] in df["user_id"].values:
        return False  # already exists

    # Append new row
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(CSV_FILE, index=False, encoding="utf-8-sig")
    return True


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""
    username = message.from_user.username or ""
    text = message.text or ""
    ts = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")

    row = {
        "user_id": user_id,
        "first_name": first_name,
        "last_name": last_name,
        "username": username,
        "message": text,
        "time": ts,
    }

    inserted = append_to_csv_unique(row)

    if inserted:
        bot.send_message(message.chat.id, "Your data has been recorded successfully ✅")
    else:
        bot.send_message(message.chat.id, "You are already registered 👍")


print("Bot running...")
bot.infinity_polling(skip_pending=True)
