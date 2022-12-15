import sqlite3
from aiogram import types, Dispatcher
from keyboards import keyboard_no_registered
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

con = sqlite3.connect("DataBases/MainDb.db")
cur = con.cursor()


def checkExistenceOfUser(userId):
    global cur
    cur.execute(f"SELECT userId FROM users WHERE userId = {str(userId)}")
    if cur.fetchone():
        return True
    else:
        return False


async def addNewUserToDB(message):
    global cur
    # cur.execute(f"SELECT userId FROM users WHERE userId = {str(message.from_user.id)}")
    if checkExistenceOfUser(message.from_user.id):
        print('User is already in database')
    else:
        cur.executemany('INSERT INTO users (name, userId) VALUES(?, ?)',
                        [(message.from_user.first_name, message.from_user.id)])
        con.commit()
        print('User has been added to database')


async def startMenu(message: types.Message):
    if not checkExistenceOfUser(message.from_user.id):
        btn = keyboard_no_registered.startRegBtn
        await message.answer("Приветствуем", reply_markup=btn)


class FSMAdmin(StatesGroup):
    name = State()
    roleType = State()


async def startReg(call: types.CallbackQuery):
    await call.message.answer("ВЫ НАЧАЛИ РЕГИСТРАЦИЮ\n"
                              "Введите ваше имя и фамилию")
    await FSMAdmin.name.set()


async def setName(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    btn = keyboard_no_registered.roleTypeBtn
    await FSMAdmin.next()
    await message.answer("Выберите вашу роль", reply_markup=btn)


async def setRoleHeadman(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['role'] = 'headman'
    await FSMAdmin.next()


def register_handlers_other(dp: Dispatcher):
    dp.register_message_handler(startMenu, commands=['start'])
    dp.register_callback_query_handler(text='startReg', callback=startReg, state=None)
    dp.register_message_handler(setName, state=FSMAdmin.name)
    dp.register_callback_query_handler(text='setHeadman', callback=setRoleHeadman, state=FSMAdmin.roleType)
