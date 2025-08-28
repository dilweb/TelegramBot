import json
import telebot
from telebot.types import Message
from telebot import custom_filters
from telebot.storage import StateMemoryStorage

import api
from config import BOT_TOKEN
from states import States

state_storage = StateMemoryStorage()

bot = telebot.TeleBot(BOT_TOKEN, state_storage=state_storage)

@bot.message_handler(commands=['start'])
def start(message: Message) -> None:
    bot.send_message(
        message.chat.id,
        'Hello! I\'m a bot powered by Merriam-Webster. I can clarify the meaning of any English word. To get started, type /lookup.',
        parse_mode='HTML',
    )
    bot.set_state(message.from_user.id, States.base, message.chat.id)


@bot.message_handler(commands=['lookup'])
def lookup_cmd(message: Message) -> None:
    bot.send_message(message.chat.id, f'Send me a word and I\'ll give you its definition.')
    bot.set_state(message.from_user.id, States.lookup, message.chat.id)


@bot.message_handler(state=States.lookup)
def lookup(message: Message) -> None:
    res = api.lookup(message.text)

    if "error" in res:
        bot.reply_to(message, "Nothing found. Check the word or try another one.")
        return

    if "suggestions" in res:
        sug = ", ".join(res["suggestions"])
        bot.reply_to(message, f"No exact match found.\nDid you mean: {sug}")
        return

    # нормальный ответ
    pos  = (res["pos"] or "")
    pron = res.get("pron") or ""
    if pron:
        pron = f'🗣  [{pron}]'
    else:
        pron = ""
    sdef = res["shortdef"]
    bot.reply_to(
        message,
        f"<b>{res['word']}</b> — {pos}\n{pron}\n\n"
        f"Short definition:\n<em>{sdef}</em>",
        parse_mode="HTML"
    )



if __name__ == '__main__':
    bot.add_custom_filter(custom_filters.StateFilter(bot))
    bot.set_my_commands([
        telebot.types.BotCommand("start", "To start"),
        telebot.types.BotCommand("lookup", "To get full definition")
    ])
    bot.polling()