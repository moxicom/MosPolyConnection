from aiogram import types, Dispatcher
from start_bot import dp, bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import sqlite3

con = sqlite3.connect("DataBases/MainDb.db")
cur = con.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS messages(message_ID integer PRIMARY KEY, title TEXT, message TEXT)''')
con.commit()

glob_title = ''


class FSMAdmin(StatesGroup):
    title = State()
    text = State()


# начало диалога добавления сообщения
# @dp.message_handler(commands=['добавить'], state=None)
async def msg_start(message: types.Message):
    await FSMAdmin.title.set()
    await message.reply('Введите заголовок')


# @dp.message_handler(content_types=['text'], state=FSMAdmin.title)
async def msg_set_title(message: types.Message, state: FSMContext):
    global glob_title
    glob_title = message.text
    con.commit()
    async with state.proxy() as data:
        data['title'] = message.text
    await FSMAdmin.next()
    await message.reply('Теперь введите текст')
    print('second message has been recived')


# @dp.message_handler(state=FSMAdmin.text)
async def msg_set_text(message: types.Message, state: FSMContext):
    cur.executemany("INSERT INTO messages (title, message) VALUES(?, ?)", [(glob_title, message.text)])
    con.commit()
    async with state.proxy() as data:
        data['text'] = message.text

    async with state.proxy() as data:
        await message.reply(str(data))
    await state.finish()
    print('third message has been recived')


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(msg_start, commands=['добавить'], state=None)  # , commands = [ , ]
    dp.register_message_handler(msg_set_title, state=FSMAdmin.title)
    dp.register_message_handler(msg_set_text, state=FSMAdmin.text)
