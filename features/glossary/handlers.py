import logging
from telebot.types import Message, CallbackQuery
from features.glossary.keyboards import gen_markup
import infra.dictionary_api as api
from features.glossary import repo
from features.glossary import repo_thesaurus as trepo

logger = logging.getLogger(__name__)

def setup_handlers(bot):
    """
    Тащим все хендлеры в __main__ одной функцией.
    Передаем нашего бота
    """

    @bot.message_handler(commands=['start'])
    def start(message: Message) -> None:
        logger.info("Received /start from user %s", message.from_user.id)
        bot.send_message(
            message.chat.id,
            'Hello! I\'m a bot powered by Merriam-Webster.\n'
            'I can clarify the meaning of any English word.\n\n'
            'To get started, type any word (or use /lookup for a hint).',
            parse_mode='HTML',
        )


    @bot.message_handler(commands=['lookup'])
    def lookup_cmd(message: Message) -> None:
        logger.info("Received /lookup from user %s", message.from_user.id)
        bot.send_message(message.chat.id, 'Type a word to look it up.')


    @bot.message_handler(content_types=['text'])
    def do_lookup(message: Message) -> None:
        logger.info("Received text '%s' from user %s", message.text, message.from_user.id)
        text = (message.text or '').strip()
        if not text or text.startswith('/'):
            return

        cached = repo.get_word(text)
        if cached:
            logger.info("Found cached word %s", text)
            res = cached
        else:
            logger.info("Looking up word %s", text)

            res = api.fetch_definition(message.text)

            if "error" in res:
                bot.reply_to(message, "Nothing found. Check the word or try another one.")
                return

            if "suggestions" in res:
                sug = ", ".join(res["suggestions"])
                bot.reply_to(message, f"No exact match found.\nDid you mean: {sug}")
                return

            try:
                repo.save_word(text, res)
            except Exception as e:
                logger.warning("Failed to save '%s' to DB: %s", text, e)


        # готовый ответ
        pos = res["pos"] or ""
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
                formed_string += f'● {definition}.'
            else:
                formed_string += f'● {definition};\n'

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
            pass # если клавы уже нет то ок

        # достаем из колбэка слово для поиска
        _, word = callback_query.data.split("|", 1)

        # ищем в кеше
        cached = trepo.get_syn_ant(word)
        if cached:
            logger.info("Found cached word %s", word)
            res = cached
        else:
            res = api.fetch_thesaurus(word)

            if isinstance(res, dict) and 'error' in res:
                bot.send_message(callback_query.message.chat.id, 'Sorry, can\'t find any.')
                return

            try:
                trepo.save_syn_ant(word, res)
            except Exception as e:
                logger.warning("Failed to save thesaurus '%s' to DB: %s", word, e)

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

