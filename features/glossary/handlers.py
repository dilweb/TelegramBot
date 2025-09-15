import logging
from telebot.types import Message, CallbackQuery
import infra.dictionary_api as api
from features.glossary import repo
from features.glossary import repo_thesaurus as trepo
from features.glossary import repo_ai as grepo
from features.glossary.keyboards import kb_both, kb_only_gen, kb_only_syn_ant
from infra.llm_chatgpt import ask_gpt

logger = logging.getLogger(__name__)

def setup_handlers(bot):
    """
    Тащим все хендлеры в __main__ одной функцией.
    Передаем нашего бота
    """

    @bot.message_handler(commands=["start"])
    def start(message: Message) -> None:
        logger.info("Received /start from user %s", message.from_user.id)
        bot.send_message(
            message.chat.id,
            "Hello! I'm a bot powered by Merriam-Webster.\n"
            "I can clarify the meaning of any English word.\n\n"
            "To get started, type any word (or use /help for a hint).",
            parse_mode='HTML',
        )


    @bot.message_handler(commands=["help"])
    def lookup_cmd(message: Message) -> None:
        logger.info("Received /lookup from user %s", message.from_user.id)
        bot.send_message(message.chat.id, "Don't know what to do? Just type 'susurrus' for example.")


    @bot.message_handler(content_types=["text"])
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
            pron = f"🗣  [{pron}]"
        else:
            pron = ""

        # форматируем список под вывод
        sdef = res["shortdef"]
        formed_string = ''
        for i, definition in enumerate(sdef):
            if i == len(sdef) - 1:
                formed_string += f"● {definition}."
            else:
                formed_string += f"● {definition};\n"

        bot.reply_to(
            message,
            f"<u><b>{res['word']}</b> — {pos}</u>\n{pron}\n\n"
            f"Short definitions:\n<em>{formed_string}</em>",
            parse_mode="HTML",
            reply_markup=kb_both(message.text.strip().lower()),
        )


    @bot.callback_query_handler(
        func=lambda callback_query: (callback_query.data.startswith("syn_ant|"))
        )
    def syn_ant_answer(callback_query: CallbackQuery) -> None:

        # фиксируем нажатие кнопки и убираем индикатор загрузки
        bot.answer_callback_query(callback_query.id)

        try:
            _, word, remain = callback_query.data.split("|", 2)
        except ValueError:
            parts = callback_query.data.split("|", 1)
            word, remain = parts[1], "gen"

        # удаляем клавиатуру у исходного меседжа
        try:
            bot.edit_message_reply_markup(
                callback_query.message.chat.id,
                callback_query.message.message_id,
                reply_markup=None
            )
        except Exception:
            pass # если клавы уже нет то ок

        # ищем в кеше
        cached = trepo.get_syn_ant(word)
        if cached:
            logger.info("Found cached word %s", word)
            res = cached
        else:
            res = api.fetch_thesaurus(word)

            if isinstance(res, dict) and "error" in res:
                logger.warning("NO SYN ANT for word %s", word)

            try:
                trepo.save_syn_ant(word, res)
            except Exception as e:
                logger.warning("Failed to save thesaurus '%s' to DB: %s", word, e)


        syns = ", ".join(res["synonyms"]) if res.get("synonyms") else "No synonyms available."
        ants = ", ".join(res["antonyms"]) if res.get("antonyms") else "No antonyms available."
        text = f"<b>Synonyms</b>: {syns}\n<b>Antonyms</b>: {ants}"

        if remain == "gen":
            bot.send_message(callback_query.message.chat.id, text, parse_mode="HTML", reply_markup=kb_only_gen(word))
        elif remain == "none":
            bot.send_message(callback_query.message.chat.id, text, parse_mode="HTML")
        else:
            bot.send_message(callback_query.message.chat.id, text, parse_mode="HTML", reply_markup=kb_only_syn_ant(word))


    @bot.callback_query_handler(
        func=lambda callback_query: (callback_query.data.startswith("gen_sent|"))
    )
    def generate_sentence(callback_query: CallbackQuery) -> None:
        bot.answer_callback_query(callback_query.id)

        try:
            _, word, remain = callback_query.data.split("|", 2)
        except ValueError:
            parts = callback_query.data.split("|", 1)
            word, remain = parts[1], "syn"

        # удаляем клавиатуру у исходного меседжа
        try:
            bot.edit_message_reply_markup(
                callback_query.message.chat.id,
                callback_query.message.message_id,
                reply_markup=None
            )
        except Exception:
            pass  # если клавы уже нет то ок

        cached = grepo.get_sentence(word)
        if cached:
            logger.info("Found cached sentence for: %s", word)
            sentence = cached
        else:
            sentence = ask_gpt(word).strip()
            try:
                grepo.save_sentence(word, sentence)
            except Exception as e:
                logger.warning("Failed to save sentence '%s' to DB: %s", word, e)

        word = (word or "").strip()
        logger.info("Generating example sentence with word='%s' for user %s",
                    word, callback_query.from_user.id)


        if not sentence:
            sentence = f"Could not generate a sentence with '{word}'. Try again later."

        if remain == "syn":
            bot.send_message(callback_query.message.chat.id, sentence, parse_mode="HTML", reply_markup=kb_only_syn_ant(word))
        elif remain == "none":
            bot.send_message(callback_query.message.chat.id, sentence, parse_mode="HTML")
        else:
            bot.send_message(callback_query.message.chat.id, sentence, reply_markup=kb_only_gen(word))

