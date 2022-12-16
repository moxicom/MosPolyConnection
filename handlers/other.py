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


async def addNewUserToDB(message, name):
    global cur
    cur.execute(f"SELECT userId FROM users WHERE userId = {str(message.from_user.id)}")
    if checkExistenceOfUser(message.from_user.id):
        print('User is already in database')
    else:
        cur.executemany('INSERT INTO users (name, userId) VALUES(?, ?)',
                        [(name, message.from_user.id)])
        con.commit()
        print('User has been added to database')


async def startMenu(message: types.Message):
    if not checkExistenceOfUser(message.from_user.id):
        btn = keyboard_no_registered.startRegBtn
        await message.answer("Приветствуем", reply_markup=btn)
    else:
        await message.answer("Мы рады вашему возвращению")


class FSMAdmin(StatesGroup):
    name = State()
    roleType = State()
    group = State()


async def startReg(call: types.CallbackQuery):
    await call.message.answer("ВЫ НАЧАЛИ РЕГИСТРАЦИЮ")
    await call.message.answer("ВВЕДИТЕ ИМЯ И ФАМИЛИЮ")
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
    await call.message.answer("Введите номер вашей группы")
    await FSMAdmin.next()


async def setRoleMember(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['role'] = 'member'
    await call.message.answer("Введите номер вашей группы")
    await FSMAdmin.next()


async def setGroup(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        async with state.proxy() as data:
            data['group'] = message.text
        await message.answer(f"Вас зовут: {data['name']}\n Вы: {data['role']}\n Вы из группы: {data['group']}")
        await addNewUserToDB(message, data['name'])
        await state.finish()
    else:
        await message.answer("Номер группы должен состоять только из цифр")
        await FSMAdmin.group.set()




def register_handlers_other(dp: Dispatcher):
    dp.register_message_handler(startMenu, commands=['start'])
    dp.register_callback_query_handler(text='startReg', callback=startReg, state=None)
    dp.register_message_handler(setName, state=FSMAdmin.name, content_types=types.ContentTypes.TEXT)
    dp.register_callback_query_handler(text='setHeadman', callback=setRoleHeadman, state=FSMAdmin.roleType)
    dp.register_callback_query_handler(text='member', callback=setRoleMember, state=FSMAdmin.roleType)
    dp.register_message_handler(setGroup, state=FSMAdmin.group, content_types=types.ContentTypes.TEXT)
