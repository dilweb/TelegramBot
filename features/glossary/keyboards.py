from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def kb_both(word: str) -> InlineKeyboardMarkup:
    # создаем объект клавиатуры под первое сообщение
    kb = InlineKeyboardMarkup()
    # создаем объекты кнопки
    kb.add(InlineKeyboardButton(
        text='Show synonyms or antonyms',
        callback_data=f'syn_ant|{word}|gen')
    )

    kb.add(InlineKeyboardButton(
        text='Generate a sentence',
        callback_data=f'gen_sent|{word}|syn')
    )
    return kb

def kb_only_syn_ant(word: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(
        text='Show synonyms or antonyms',
        callback_data=f'syn_ant|{word}|none')
    )
    return kb

def kb_only_gen(word: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(
        text='Generate a sentence',
        callback_data=f'gen_sent|{word}|none')
    )
    return kb