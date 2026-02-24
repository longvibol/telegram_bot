import telebot
import pandas as pd
from mytoken import TelegramConfig

bot = telebot.TeleBot(TelegramConfig().get_token())

CSV_FILE = "user_data_form.csv"
COLUMNS = ["user_id", "age", "gender","occupation"]

user_date = pd.read_csv(CSV_FILE)

@bot.message_handler(func=lambda message: True)
def send_welcome(message):
    bot.send_message(message.chat.id,"សួរស្តី ដើម្បីបានមេរៀន Free ខ្ញសុំព័ត៌មានខ្លះៗ? អាយុ ")
    bot.register_next_step_handler(message, process_age)

def process_age(message):
    age =  message.text
    bot.send_message(message.chat.id,"ភេទៈ ")
    bot.register_next_step_handler(message, process_gender, age)

def process_gender(message, age):
    global user_date
    gender = message.text

    bot.send_message(message.chat.id,'របរៈ សិស្ស ឬ ធ្វើការ')
    bot.register_next_step_handler(message, process_occupation, age, gender)

def process_occupation(message, age, gender):
    global user_date
    occupation = message.text


    new_date = pd.DataFrame({'user_id': [message.chat.id], 'age':[age], 'gender':[gender], 'occupation':[occupation]})
    user_date = pd.concat([user_date, new_date], ignore_index=True)
    user_date.to_csv(CSV_FILE, index=False)

    bot.send_message(message.chat.id,"Thank you! Your data have been saved !")


print("Bot running...")
bot.infinity_polling(skip_pending=True)