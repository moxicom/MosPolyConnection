from aiogram import types, Dispatcher
from start_bot import dp, bot


# @dp.message_handler()
async def echo(message: types.Message):
    # await message.answer(message.text)
    await message.reply(message.text)
    print(list(message))
    print(message.from_user.id)


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(echo)  # , commands = [ , ]
