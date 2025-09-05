import telebot
import logging
from core.config import BOT_TOKEN
from core.logger import setup_logging
from core.db import init_db, clear_old_cache, reset_cache
from features.glossary.router import register_glossary_handlers

setup_logging()   # включаем логи
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(BOT_TOKEN)

def main():
    # reset_cache()
    init_db()

    # разовая уборка на старте
    clear_old_cache(30)

    # подключаем все хендлеры и фичи
    register_glossary_handlers(bot)

    logger.info("Starting Telegram Bot...")

    bot.set_my_commands([
        telebot.types.BotCommand("start", "To start"),
        telebot.types.BotCommand("lookup", "How to use")
    ])

    logger.info("Bot started. Waiting for updates...")

    bot.infinity_polling()

if __name__ == '__main__':
    main()