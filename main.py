# import telebot
# from telebot import types
# import datetime
#
# token = "5555273889:AAEIPROI8yHpqORNoUlffMxC_qWpFMvEfEw"
# bot = telebot.TeleBot(token)
#
#
# @bot.message_handler(commands=['start', 'help'])
# def send_welcome(message):
#     bot.reply_to(message, "Howdy, how are you doing?")
#
#
# @bot.message_handler(func=lambda m: True)
# def echo_all(message):
#     bot.reply_to(message, message.text)
#
#
# @bot.message_handler(commands=['button'])
# def button_message(message):
#     markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     item1 = types.KeyboardButton("Кнопка")
#     markup.add(item1)
#     bot.send_message(message.chat.id, "Выбирите нужный пункт", reply_markup=markup)
#
# bot.infinity_polling()

import sqlite3
from sqlite3 import Error as sqlError


def sql_connection(name):
    try:
        connection = sqlite3.connect(name)
        print("Connection is done")
        return connection
    except sqlError:
        print(sqlError)


def sql_table(connection):
    cursorObj = connection.cursor()
    try:
        cursorObj.execute(
            "CREATE TABLE employees(id integer PRIMARY KEY, text text, salary real, department text, position text, hireDate text)")
        connection.commit()
    except Exception:
        print("CREATE TABLE error sql_table")


def sql_insert(con, entities):
    cursorObj = con.cursor()
    try:
        cursorObj.execute("INSERT INTO employees(id, name, salary, department, position, hireDate) VALUES(?, ?, ?, ?, ?, ?)",
                          entities)
        con.commit()
    except Exception:
        print("INSERT error уже существует такая запись sql_insert")


connection = sql_connection("main_base.db")
sql_table(connection)
entities = (2, "Andrew", 800, "IT", "Tech", "2018-02-06")
sql_insert(connection, entities)