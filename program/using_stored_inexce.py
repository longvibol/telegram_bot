import os
import telebot
import pandas as pd
from datetime import datetime
from mytoken import TelegramConfig

bot = telebot.TeleBot(TelegramConfig().get_token())

CSV_FILE = "user_data.csv"
COLUMNS = ["user_id", "first_name", "last_name", "username", "message", "time"]

chat_data = pd.read_csv(CSV_FILE)

# for user_id in chat_data["user_id"]:
#     print(user_id)
#     bot.send_message(user_id, "Hello! This is a message from the bot.")

@bot.message_handler(func=lambda message: True)
def send_welcome(message):
    bot.send_message(message.chat.id,"Hello! This is a message from the bot.What is your age?")
    bot.register_next_step_handler(message, process_age)

def process_age(message):
    age =  message.text
    bot.send_message(message.chat.id,"What is your gender?")
    bot.register_next_step_handler(message, process_gender, age)

def process_gender(message, age):
    gender = message.text
    bot.send_message(message.chat.id,f"Thank you! Your age is {age} and your gender is {gender}")



print("Bot running...")
bot.infinity_polling(skip_pending=True)