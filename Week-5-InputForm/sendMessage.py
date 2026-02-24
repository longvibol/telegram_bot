import telebot
import pandas as pd
from mytoken import TelegramConfig

bot = telebot.TeleBot(TelegramConfig().get_token())

CSV_FILE = "user_data_form.csv"

chat_data = pd.read_csv(CSV_FILE)

for index, row in chat_data.iterrows():
    user_id = row['user_id']
    age = row['age']
    occupation = row['occupation']

    print(user_id, age, occupation)

    if(age >= 18):
        message = f"Hello! You are eligible for our services. Your occupation is {occupation}."
        print(message)
        # bot.send_message(user_id, "https://www.instagram.com/models.korea_/reel/CkRLAHtDcCh/")
        bot.send_photo(user_id,'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS0u5UYauOcjdKxOPU9gmD5dHZQ5G1Rk9DoFg&s', caption=message)

print("Bot running...")
bot.infinity_polling(skip_pending=True)