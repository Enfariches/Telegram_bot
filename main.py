import telebot
from datetime import datetime
bot = telebot.TeleBot("")

@bot.message_handler(commands=['start'])
def start(message):
	bot.send_message(message.chat.id, f"Привет сейчас {str(datetime.now().hour)}:{str(datetime.now().minute)}")

@bot.message_handler()
def get_user_message(message):
	bot.send_message(message.chat.id, "Напиши время отправки")
	while True:
		if message.text == f"{str(datetime.now().hour)}:{str(datetime.now().minute)}":
			bot.send_message(message.chat.id, "Вау, это супер")
			break

bot.polling(none_stop=True)
