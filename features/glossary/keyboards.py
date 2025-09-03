from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def gen_markup(word: str):
    # создаем объект кнопки
    syn_ant_button = InlineKeyboardButton(
        text='Show synonyms or antonyms',
        callback_data=f'syn_ant|{word}')

    # создаем объект клавиатуры и добавляем туда нашу кнопку
    kb = InlineKeyboardMarkup()
    kb.add(syn_ant_button)
    return kb