import os
import telebot
import pandas as pd
from datetime import datetime
from mytoken import TelegramConfig

bot = telebot.TeleBot(TelegramConfig().get_token())

chat_data = pd.read_csv("user_data.csv")

for user_id in chat_data['user_id']:
    print(user_id)
    bot.send_message(user_id,"Hello, I'm a Telegram bot.")


print("Bot running...")
bot.infinity_polling()
