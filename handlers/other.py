import sqlite3
from aiogram import types, Dispatcher
from keyboards import keyboard_no_registered
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from aiogram.types import ReplyKeyboardRemove

con = sqlite3.connect("DataBases/MainDb.db")
cur = con.cursor()

conGroups = sqlite3.connect("DataBases/Groups.db")
curGroups = conGroups.cursor()


def checkExistenceOfUser(userId):
    global cur
    cur.execute(f"SELECT userId FROM users WHERE userId = {str(userId)}")
    if cur.fetchone():
        return True
    else:
        return False


async def addNewUserToDB(message, name, groupNumber, role):
    global cur
    cur.execute(f"SELECT userId FROM users WHERE userId = {str(message.from_user.id)}")
    if checkExistenceOfUser(message.from_user.id):
        print('User is already in database')
    else:
        cur.executemany("INSERT INTO users (name, userId, groupNumber, role) VALUES(?, ?, ?, ?)",
                        [(name, message.from_user.id, groupNumber, role)])
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
    password = State()
    repeatPassword = State()


async def startReg(call: types.CallbackQuery):
    btn = keyboard_no_registered.stopRegBtn
    await call.message.answer("ВЫ НАЧАЛИ РЕГИСТРАЦИЮ", reply_markup=btn)
    await call.message.answer("ВВЕДИТЕ ИМЯ И ФАМИЛИЮ")
    await FSMAdmin.name.set()


async def setName(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    btn = keyboard_no_registered.roleTypeBtn
    await FSMAdmin.next()
    await message.answer("Выберите вашу роль", reply_markup=btn)


async def setRoleHeadman(call: types.CallbackQuery, state: FSMContext):
    btn = keyboard_no_registered.stopRegBtn
    async with state.proxy() as data:
        data['role'] = 'headman'
    await call.message.answer("Введите номер вашей группы", reply_markup=btn)
    await FSMAdmin.next()


async def setRoleMember(call: types.CallbackQuery, state: FSMContext):
    btn = keyboard_no_registered.stopRegBtn
    async with state.proxy() as data:
        data['role'] = 'member'
    await call.message.answer("Введите номер вашей группы", reply_markup=btn)
    await FSMAdmin.next()


async def setGroup(message: types.Message, state: FSMContext):
    global cur
    # print(f'Message text: {message.text}\n {message.text[:3]} {message.text[3]} {message.text[4:]}')
    if (message.text[:3].isdigit() and message.text[3] == '-' and message.text[4:].isdigit() and len(message.text) == 7
            and message.text[4:].isdigit()):
        async with state.proxy() as data:
            data['group'] = message.text
        # проверка на существование группы
        curGroups.execute(f" SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{data['group']}-users'")
        # add new row to DB
        fetch = curGroups.fetchone()
        print(fetch, " setGroup")
        if fetch[0] == 1:  # если группа существует
            print('Group exists')
            if data['role'] == 'headman':
                await message.answer("У этой группы уже есть создатель. Попробуйте иначе")
                await FSMAdmin.group.set()
            # вот тут надо переходить к следующему состоянию (проверка пароля, если это member или задание пароля, если это headman)
            else:
                await message.answer("Отлично, теперь введите пароль")
                await FSMAdmin.next()
                # await addNewUserToDB(message, data['name'], data['group'], data['role'])
                # await message.answer(
                #     f"ПРОФИЛЬ:\nВас зовут: {data['name']}\n Вы: {data['role']}\n Вы из группы: {data['group']}")
                # await state.finish()
        else:
            print(f"Group {data['group']} does not exist")
            if data['role'] == 'member':
                await message.answer('Такой группы не существует, Введите другой нормер группы')
                await FSMAdmin.group.set()
            if data['role'] == 'headman':
                await message.answer("Отлично, теперь введите пароль")
                await FSMAdmin.next()
                # curGroups.execute(f"CREATE TABLE '{data['group']}'('name' TEXT, 'userId' INTEGER, 'role' TEXT)")
                # conGroups.commit()
                # await message.answer(f"В базе данных была создана группа с номером {data['group']}")
    else:
        await message.answer("Неверный формат ввода. Попробуйте еще раз (например: 222-111)")
        await FSMAdmin.group.set()


async def setPassword(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['password'] = message.text
    if (len(str(data['password']).replace(' ', '')) < 6) or (
            len(str(data['password']).replace(' ', '')) != len(str(data['password']))):
        await message.answer(
            'Пароль не может состоять из меньше 6 символов и не должен содержать пробелы, введите еще раз')
        await FSMAdmin.password.set()
    else:
        if data['role'] == 'headman':
            await message.answer("Повторите пароль")
            await FSMAdmin.next()
        else:  # role == member
            cur.execute(f"SELECT password FROM groupPasswords WHERE groupNumber ='{data['group']}'")
            fetch = cur.fetchone()
            print("fetch", data['group'], fetch, " setPassword")
            if data['password'] == fetch[0]:
                await message.answer("Пароль верный")
                await addNewUserToDB(message, data['name'], data['group'], data['role'])
                curGroups.execute(f"INSERT INTO '{data['group']}-users' (name, userId, role) VALUES(?, ?, ?)",
                                  (data['name'], message.from_user.id, data['role']))
                conGroups.commit()
                await message.answer(
                    f"ПРОФИЛЬ:\nВас зовут: {data['name']}\n Вы: {data['role']}\n Вы из группы: {data['group']}")
                await state.finish()
            else:
                await message.answer("Пароль неверный, попробуйте еще раз")
                await FSMAdmin.password.set()


async def checkPassword(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['repeatPassword'] = message.text
    if data['role'] == 'headman':
        if data['password'] == data['repeatPassword']:
            curGroups.execute(f"CREATE TABLE '{data['group']}-users'('name' TEXT, 'userId' INTEGER, 'role' TEXT)")
            conGroups.commit()
            curGroups.execute(f"CREATE TABLE '{data['group']}-messages'('name' TEXT, 'userId' INTEGER, 'role' TEXT)")
            conGroups.commit()
            cur.executemany("INSERT INTO groupPasswords (groupNumber, password) VALUES(?, ?)",
                            [(data['group'], data['password'])])
            con.commit()

            curGroups.execute(f"INSERT INTO '{data['group']}-users' (name, userId, role) VALUES(?, ?, ?)",
                              (data['group'], message.from_user.id, data['role']))
            conGroups.commit()
            await message.answer('Пароль задан')
            await addNewUserToDB(message, data['name'], data['group'], data['role'])
            await message.answer(
                f"ПРОФИЛЬ:\nВас зовут: {data['name']}\n Вы: {data['role']}\n Вы из группы: {data['group']}")

            await state.finish()
        else:
            await message.answer('Пароли не совпадают. Попробуйте еще раз')
            await FSMAdmin.password.set()

    else:  # role == member
        pass


async def stopRegister(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer('Регистрация отменена', reply_markup=ReplyKeyboardRemove())


def register_handlers_other(dp: Dispatcher):
    dp.register_message_handler(startMenu, commands=['start'])
    dp.register_message_handler(stopRegister, Text(equals='Отмена регистрации', ignore_case=True), state='*')
    dp.register_callback_query_handler(text='startReg', callback=startReg, state=None)
    dp.register_message_handler(setName, state=FSMAdmin.name, content_types=types.ContentTypes.TEXT)
    dp.register_callback_query_handler(text='setHeadman', callback=setRoleHeadman, state=FSMAdmin.roleType)
    dp.register_callback_query_handler(text='member', callback=setRoleMember, state=FSMAdmin.roleType)
    dp.register_message_handler(setGroup, state=FSMAdmin.group, content_types=types.ContentTypes.TEXT)
    dp.register_message_handler(setPassword, state=FSMAdmin.password, content_types=types.ContentTypes.TEXT)
    dp.register_message_handler(checkPassword, state=FSMAdmin.repeatPassword, content_types=types.ContentTypes.TEXT)
