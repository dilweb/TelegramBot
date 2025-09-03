from features.glossary.handlers import setup_handlers
"""
Функция работает к сборщик фичей для бота, чтобы в мейне объявить один импорт и пользоваться как модулями.

"""
def register_glossary_handlers(bot):
    setup_handlers(bot)
