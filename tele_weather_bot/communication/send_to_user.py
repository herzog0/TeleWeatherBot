import telepot
import os

__bot = None


def simple_message(chat_id, message, **kwargs):
    global __bot
    if not __bot:
        __bot = telepot.Bot(os.environ.get('TELEGRAM_TOKEN', None))
    return __bot.sendMessage(chat_id, message, **kwargs)


def markdown_message(chat_id, message, **kwargs):
    return simple_message(chat_id, message, parse_mode="Markdown", **kwargs)


def html_message(chat_id, message, **kwargs):
    return simple_message(chat_id, message, parse_mode="HTML", **kwargs)


def inline_keyboard_message(chat_id, message, keyboard=None, **kwargs):
    return simple_message(chat_id, message, parse_mode="Markdown", reply_markup=keyboard, **kwargs)


def edit_message(message_id, message, keyboard=None, **kwargs):
    global __bot
    if not __bot:
        __bot = telepot.Bot(os.environ.get('TELEGRAM_TOKEN', None))
    return __bot.editMessageText(message_id, message, parse_mode="Markdown", reply_markup=keyboard, **kwargs)


def answer_callback_query(query_id, message='', **kwargs):
    global __bot
    if not __bot:
        __bot = telepot.Bot(os.environ.get('TELEGRAM_TOKEN', None))
    return __bot.answerCallbackQuery(query_id, text=message, **kwargs)


def delete_message(message_id):
    global __bot
    if not __bot:
        __bot = telepot.Bot(os.environ.get('TELEGRAM_TOKEN', None))
    return __bot.deleteMessage(message_id)
