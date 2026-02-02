import telebot

BOT_TOKEN = "8338627964:AAE5OBrqHfERvlqd-lv2dXFe_TAb_eOBiNc"
bot = telebot.TeleBot(BOT_TOKEN)

bot.send_message(211259472,"This is second message!")