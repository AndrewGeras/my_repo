import asyncio

from aiogram import Bot, Dispatcher
from config_data.config import Config, load_config
from handlers import add_words_handlers, show_dict_handlers, find_word_hendlers, other_handlers, test_words_handler
from keyboards.main_menu import set_main_menu

async def main():
    config: Config = load_config()

    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(storage=add_words_handlers.storage)

    await set_main_menu(bot)

    dp.include_router(other_handlers.router)
    dp.include_router(add_words_handlers.router)
    dp.include_router(show_dict_handlers.router)
    dp.include_router(find_word_hendlers.router)
    dp.include_router(test_words_handler.router)


    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())