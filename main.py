import time
import telebot
from telebot import types
from datetime import datetime
import sqlite3
import random

bot = telebot.TeleBot("")
brain = {}

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
startbutton = ("Создать✅", "Статус👏", "Удалить🛒", "Пуск🏁")
markup.add(*startbutton)

choice_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
choicebutton = ("Одноразовая", "Вечная")
choice_markup.add(*choicebutton)

def is_time_format(param):
    try:
        time.strptime(param, '%H:%M')
        return True
    except ValueError:
        return False

def valid_key(key):
    try:
        if brain[key] or brain[key] == []:
            return True
    except KeyError:
        return False

def open_base():
    with open('parser_list.txt', 'r') as f:
        lst_gm = f.read().split("% ")
    return lst_gm

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"Привет, {message.from_user.username} 👋 \n\nЭтот удивительный Телеграм бот отправляет вам ежедневное утреннее приветствие, чтобы начать ваш день с настроения и позитива! "
                                      f"\n\nОн отправит вам сообщение каждое утро с ласковыми словами, пожеланиями доброго дня и вдохновляющей цитатой."
                                      f" Вы можете настроить время отправки утреннего приветствия, чтобы оно соответствовало вашему расписанию."
                                      f" \n\nБлагодаря этому телеграм боту, вы будете каждое утро просыпаться с положительным настроением и уверенностью в том, что доброе утро ждет вас! \n(_Описание написано ChatGPT_)",
                     parse_mode="Markdown", reply_markup=markup)
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
	id INTEGER UNIQUE,
	first_name STRING,
	last_name STRING,
	username STRING
	)""")
    connect.commit()
    user_list = [message.chat.id, message.from_user.first_name, message.from_user.last_name, message.from_user.username]
    cursor.execute(f"INSERT OR IGNORE INTO users VALUES(?,?,?,?);", user_list)
    connect.commit()

@bot.message_handler(content_types=["text"])
def bot_message(message):
    if message.text == "Создать✅":
        setup(message)
    if message.text == "Статус👏":
        if valid_key(message.chat.id) and brain[message.chat.id] != []:
            status(message)
        else:
            bot.send_message(message.chat.id, f"Нет активных напоминалок",
                             reply_markup=markup)
    if message.text == "Удалить🛒":
        if valid_key(message.chat.id) and brain[message.chat.id] != []:
            delete(message)
        else:
            bot.send_message(message.chat.id, f"Нет активных напоминалок",
                             reply_markup=markup)
    if message.text == "Пуск🏁":
        if valid_key(message.chat.id) and brain[message.chat.id] != []:
            msg = bot.send_message(message.chat.id, "Одноразовая или Вечная", reply_markup=choice_markup)
            bot.register_next_step_handler(msg, runtime)
        else:
            bot.send_message(message.chat.id, f"Нет активных напоминалок",
                             reply_markup=markup)


def status(message):
    bot.send_message(message.chat.id, f'Ваши напоминалки:\n{", ".join(i for i in brain[message.chat.id])}',
                         reply_markup=markup)


def setup(message):
    msg = bot.send_message(message.chat.id, "Введите время в формате (Чч:Мм)")
    bot.register_next_step_handler(msg, add_to_base)


def add_to_base(message):
    if is_time_format(message.text) and valid_key(message.chat.id) == False:
        brain[message.chat.id] = []
        brain[message.chat.id].append(message.text)
        bot.send_message(message.chat.id, "Ваше время записно, "
                                          "если хотите записать ещё одно время вызовите функцию заново",
                         reply_markup=markup)

    elif is_time_format(message.text) and valid_key(message.chat.id):
        brain[message.chat.id].append(message.text)
        bot.send_message(message.chat.id, "Ваше время записно ещё, "
                                          "если хотите записать ещё одно время вызовите функцию заново",
                         reply_markup=markup)

    elif message.text == "Статус👏":
        bot_message(message)

    elif message.text == "Удалить🛒":
        bot_message(message)

    elif message.text == "Пуск🏁":
        bot_message(message)

    elif message.text[0] == '/':
        bot_message(message)

    else:
        bot.send_message(message.chat.id, "Неверный формат или ваше время уже в списке",
                         reply_markup=markup)
        time.sleep(1)
        setup(message)


def delete(message):
    time_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    timebutton = (i for i in brain[message.chat.id])
    time_markup.add(*timebutton, "Отмена")
    msg = bot.send_message(message.chat.id, f"Какую напоминалку удалить? \n", reply_markup=time_markup)
    bot.register_next_step_handler(msg, delete_to_base)


def delete_to_base(message):
    if is_time_format(message.text) and valid_key(message.chat.id):
        brain[message.chat.id].remove(message.text)
        bot.send_message(message.chat.id, "Успешно", reply_markup=markup)
    elif message.text == "Статус👏":
        bot_message(message)
    elif message.text == "Удалить🛒":
        bot_message(message)
    elif message.text == "Пуск🏁":
        bot_message(message)
    elif message.text[0] == '/':
        bot_message(message)
    elif message.text == "Отмена":
        bot.send_message(message.chat.id, "Отмена удаления", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Неправильный формат или времени нет в списке", reply_markup=markup)
        time.sleep(1)
        delete(message)


def runtime(message):
    choice = message.text
    if choice == 'Одноразовая' or choice == 'Вечная':
        bot.send_message(message.chat.id, "Процесс напоминалок запущен! 🚀", reply_markup=markup)
        brain_sorted = sorted(brain[message.chat.id])
        lst_gm = open_base()
        while True:
            now = datetime.now().strftime("%H:%M")
            if brain_sorted[0] == now:
                if choice == 'Одноразовая':
                    bot.send_message(message.chat.id, f"{lst_gm[random.randint(1, 390)] + ' ❤️'}", reply_markup=markup)
                    brain_sorted.pop(0)
                    brain[message.chat.id].pop(0)
                    if len(brain_sorted) != 0:
                        runtime(message)
                    bot.send_message(message.chat.id, "Напоминалок больше нет", reply_markup=markup)
                    break
                bot.send_message(message.chat.id, f"{lst_gm[random.randint(1, 390)] + ' ❤️'}", reply_markup=markup)
                time.sleep(61)
            brain_sorted = sorted(brain[message.chat.id])
            if len(brain_sorted) == 0:
                bot.send_message(message.chat.id, "Вы удалили из процесса все напоминалки", reply_markup=markup)
                break
    else:
        bot_message(message)


bot.polling(none_stop=True)
