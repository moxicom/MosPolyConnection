from aiogram.utils import executor
from start_bot import dp

from handlers import client, admin, other


def on_startup():
    print("Bot was started")


other.register_handlers_other(dp)
admin.register_handlers_admin(dp)
client.register_handlers_client(dp)

executor.start_polling(dp, skip_updates=True, on_startup=on_startup())
