import time
import telebot
from telebot import types
from datetime import datetime
import sqlite3
import random
import threading
import pytz

bot = telebot.TeleBot("5625878280:AAF4kWU1MXmuzn759huVQsWzTnG7b0tA1Jo")
timer = {}

markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
menubutton = ("Создать✅", "Статус👏", "Удалить🛒", "Пуск🏁")
markup.add(*menubutton)

start_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
startbutton = ("Создать✅")
start_markup.add(startbutton)

choice_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
choicebutton = ("Одноразовая", "Вечная")
choice_markup.add(*choicebutton)


def database_work(message):
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS users(
        	id INTEGER UNIQUE,
        	first_name STRING,
        	last_name STRING,
        	username STRING,
        	reminder_time TEXT,
        	reminder_status STRING,
        	secret_answer STRING
        	)""")
    connect.commit()
    user_list = [message.chat.id, message.from_user.first_name, message.from_user.last_name,
                 message.from_user.username, None, 'Нет формата', None]
    cursor.execute(f"INSERT OR IGNORE INTO users VALUES(?,?,?,?,?,?,?);", user_list)
    connect.commit()

def is_time_format(param):
    try:
        time.strptime(param, '%H:%M')
        return True
    except ValueError:
        return False

def open_base():
    with open('parser_list.txt', 'r', encoding='utf-8') as f:
        lst_gm = f.read().split("Z ")
    return lst_gm

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"Привет, {message.from_user.username} 👋 \n\nЭтот удивительный Телеграм бот отправляет вам ежедневное утреннее приветствие, чтобы начать ваш день с настроения и позитива! "
                                      f"\n\nОн отправит вам сообщение каждое утро с ласковыми словами, пожеланиями доброго дня и вдохновляющей цитатой."
                                      f" Вы можете настроить время отправки утреннего приветствия, чтобы оно соответствовало вашему расписанию."
                                      f" \n\nБлагодаря этому телеграм боту, вы будете каждое утро просыпаться с положительным настроением и уверенностью в том, что доброе утро ждет вас! \n(_Описание написано ChatGPT_)",
                     parse_mode="Markdown", reply_markup=start_markup)
    database_work(message)

@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, "Существующие команды: \n /help \n /start \n /secret", reply_markup=markup)

@bot.message_handler(commands=['secret'])
def secret_message(message):
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    cursor.execute(f"SELECT secret_answer FROM users WHERE id = {message.chat.id}")

    if cursor.fetchone()[0] is None:
        secret_msg = bot.send_message(message.chat.id, "Кого я люблю? (1 попытка)")
        bot.register_next_step_handler(secret_msg, secret_answer)
    else:
        bot.send_message(message.chat.id, "Попытка была", reply_markup=markup)

def secret_answer(message):
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    cursor.execute(f"UPDATE users SET secret_answer = ? WHERE id = ?",
                   (message.text, message.chat.id))
    connect.commit()

    if message.text == '' or message.text == '':
        bot.send_message(message.chat.id, "", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Неа", reply_markup=markup)


@bot.message_handler(content_types=["text"])
def bot_message(message):
    if message.text == "Создать✅":
        setup(message)
    if message.text == "Статус👏":
        status(message)
    if message.text == "Удалить🛒":
        delete(message)
    if message.text == "Пуск🏁":
        msg = bot.send_message(message.chat.id, "Одноразовая или Вечная", reply_markup=choice_markup)
        bot.register_next_step_handler(msg, timer_start)


def status(message):
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    cursor.execute(f"SELECT reminder_time, reminder_status FROM users WHERE id = {message.chat.id}")
    result_status = cursor.fetchone()
    bot.send_message(message.chat.id, f'Ваше время:\n{result_status[0]} - {result_status[1]}')



def setup(message):
    msg = bot.send_message(message.chat.id, "Введите время в формате (Чч:Мм)")
    bot.register_next_step_handler(msg, add_to_base)


def add_to_base(message):

    if is_time_format(message.text):
        connect = sqlite3.connect('database.db')
        cursor = connect.cursor()
        cursor.execute(f"UPDATE users SET reminder_time = ?, reminder_status = ? WHERE id = ?",
                       (message.text, 'Нет формата', message.chat.id))
        connect.commit()
        bot.send_message(message.chat.id, "Ваше время записно",
                         reply_markup=markup)

    elif message.text == "Статус👏":
        bot_message(message)
    elif message.text == "Удалить🛒":
        bot_message(message)
    elif message.text == "Пуск🏁":
        bot_message(message)
    elif message.text == '/start':
        start(message)

    else:
        bot.send_message(message.chat.id, "Неверный формат",
                         reply_markup=start_markup)
        time.sleep(1)
        setup(message)


def delete(message):
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    cursor.execute(f"SELECT reminder_time FROM users WHERE id = {message.chat.id}")
    result = cursor.fetchone()

    time_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    time_markup.add(*result, "Отмена")

    msg = bot.send_message(message.chat.id, f"Удалить? \n", reply_markup=time_markup)
    bot.register_next_step_handler(msg, delete_to_base)


def delete_to_base(message):
    global timer
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()

    if is_time_format(message.text):
        cursor.execute("UPDATE users SET reminder_time = ? WHERE id = ?", (None, message.chat.id))
        connect.commit()
        try:
            if timer[message.chat.id]:
                timer[message.chat.id].cancel()
        except KeyError:
            pass
        bot.send_message(message.chat.id, "Удалено", reply_markup=start_markup)
        setup(message)
    elif message.text == "Статус👏":
        bot_message(message)
    elif message.text == "Удалить🛒":
        bot_message(message)
    elif message.text == "Пуск🏁":
        bot_message(message)
    elif message.text == '/start':
        bot_message(message)
    elif message.text == "Отмена":
        bot.send_message(message.chat.id, "Отмена удаления", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Неправильный формат", reply_markup=markup)
        time.sleep(1)
        delete(message)


def runtime(message):
    lst_gm = open_base()
    bot.send_message(message.chat.id, f"{lst_gm[random.randint(1, 390)] + ' ❤️'}", reply_markup=markup)
    if message.text == 'Вечная':
        time.sleep(61)
        timer_start(message)
    else:
        connect = sqlite3.connect('database.db')
        cursor = connect.cursor()
        cursor.execute(f"UPDATE users SET reminder_time = ?, reminder_status = ? WHERE id = ?",
                       (None, 'Нет формата', message.chat.id))
        connect.commit()
        bot.send_message(message.chat.id, "Установите время", reply_markup=start_markup)

def timer_start(message):
    connect = sqlite3.connect('database.db')
    cursor = connect.cursor()
    cursor.execute("UPDATE users SET reminder_status = ? WHERE id = ?", (message.text, message.chat.id))
    connect.commit()
    cursor.execute(f"SELECT reminder_time FROM users WHERE id = {message.chat.id}")
    reminder_time = cursor.fetchone()[0]

    now = datetime.now(pytz.timezone('Asia/Yekaterinburg')).strftime("%H:%M")
    delta = datetime.strptime(reminder_time, "%H:%M") - datetime.strptime(now, "%H:%M")
    timer[message.chat.id] = threading.Timer(float(delta.seconds), runtime, [message])
    timer[message.chat.id].start()
    bot.send_message(message.chat.id, "Процесс запущен! 🚀", reply_markup=markup)

bot.polling(none_stop=True)
