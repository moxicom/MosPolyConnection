from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton

startRegBtn = InlineKeyboardMarkup().add(InlineKeyboardButton(text='Зарегистрироваться', callback_data='startReg'))

stopRegBtn = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(text='Отмена регистрации'))

roleTypeBtn = InlineKeyboardMarkup()
roleTypeBtn.add(InlineKeyboardButton(text='Я участник группы', callback_data='member'))
roleTypeBtn.add(InlineKeyboardButton(text='Я староста', callback_data='setHeadman'))

