import telebot
import logging

# (Optional) helps show what's happening in the console
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8338627964:AAE5OBrqHfERvlqd-lv2dXFe_TAb_eOBiNc"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=["start", "hello"])
def send_welcome(message):

    user_name = message.from_user.first_name
    user_id = message.from_user.id

    # bot.reply_to(message, "Hello, " + user_name + "!\nYour ID is: " + str(user_id))
    bot.send_chat_action(user_id, 'typing')
    bot.send_message(user_id, "Hello, " + user_name + "!\nYour ID is: " + str(user_id))

bot.infinity_polling()
