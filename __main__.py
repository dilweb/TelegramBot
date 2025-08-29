import telebot
from telebot.types import Message, CallbackQuery
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import api
from config import BOT_TOKEN

def gen_markup(word: str):
    # создаем объект кнопки
    syn_ant_button = InlineKeyboardButton(
        text='Show synonyms or antonyms',
        callback_data=f'syn_ant|{word}')

    # создаем объект клавиатуры и добавляем туда нашу кнопку
    kb = InlineKeyboardMarkup()
    kb.add(syn_ant_button)
    return kb

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

    # готовый ответ
    pos  = (res["pos"] or "")
    pron = res.get("pron") or ""
    if pron:
        pron = f'🗣  [{pron}]'
    else:
        pron = ""

    # форматируем список под вывод
    sdef = res["shortdef"]
    formed_string = ''
    for i, definition in enumerate(sdef):
        if i == len(sdef) - 1:
            formed_string += f'{definition}.'
        else:
            formed_string += f'{definition};\n'

    bot.reply_to(
        message,
        f"<u><b>{res['word']}</b> — {pos}</u>\n{pron}\n\n"
        f"Short definitions:\n<em>{formed_string}</em>",
        parse_mode="HTML",
        reply_markup=gen_markup(res['word'])
    )

@bot.callback_query_handler(
    func=lambda callback_query: (callback_query.data.startswith('syn_ant|'))
    )
def syn_ant_answer(callback_query: CallbackQuery) -> None:
    # убираем «часики» на кнопке
    bot.answer_callback_query(callback_query.id)

    # удаляем клавиатуру у исходного меседжа
    try:
        bot.edit_message_reply_markup(
            callback_query.from_user.id,
            callback_query.message.message_id,
            reply_markup=None
        )
    except Exception:
        pass #если клавы уже нет то ок

    _, word = callback_query.data.split("|", 1)

    res = api.thesaurus(word)

    if isinstance(res, dict) and 'error' in res:
        bot.send_message(callback_query.message.chat.id, 'Sorry, can\'t find any.')
        return

    syns = res["synonyms"]
    if syns is None:
        syns = 'No synonyms available.'
    else:
        syns = ", ".join(syns)

    ants = res["antonyms"]
    if ants is None:
        ants = 'No antonyms available.'
    else:
        ants = ", ".join(ants)

    bot.send_message(
        callback_query.message.chat.id,
        f"<b>Synonyms</b>: {syns}\n\n<b>Antonyms</b>: {ants}",
        parse_mode="HTML"
        )

if __name__ == '__main__':
    bot.set_my_commands([
        telebot.types.BotCommand("start", "To start"),
        telebot.types.BotCommand("lookup", "How to use")
    ])
    bot.polling()