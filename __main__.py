import telebot
from telebot.types import Message

import api
from config import BOT_TOKEN



bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message: Message) -> None:
    bot.send_message(
        message.chat.id,
        'Hello! I\'m a bot powered by Merriam-Webster.\n'
        'I can clarify the meaning of any English word.\n\n'
        'To get started, type any word (or use /lookup for a hint).',
        parse_mode='HTML',
    )


@bot.message_handler(commands=['lookup'])
def lookup_cmd(message: Message) -> None:
    bot.send_message(message.chat.id, 'Type a word to look it up.')


@bot.message_handler(content_types=['text'])
def do_lookup(message: Message) -> None:
    if message.text.startswith('/'):
        return

    res = api.definition(message.text)

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
    bot.set_my_commands([
        telebot.types.BotCommand("start", "To start"),
        telebot.types.BotCommand("lookup", "How to use")
    ])
    bot.polling()