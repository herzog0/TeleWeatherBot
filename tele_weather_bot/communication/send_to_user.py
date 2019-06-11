import telepot
from TOKENS_HERE import TELEGRAM_TOKEN


def simple_message(chat_id, message, **kwargs):
    return telepot.Bot(TELEGRAM_TOKEN).sendMessage(chat_id, message, **kwargs)


def markdown_message(chat_id, message, **kwargs):
    return simple_message(chat_id, message, parse_mode="Markdown", **kwargs)


def html_message(chat_id, message, **kwargs):
    return simple_message(chat_id, message, parse_mode="HTML", **kwargs)


def inline_keyboard_message(chat_id, message, keyboard=None, **kwargs):
    return simple_message(chat_id, message, parse_mode="Markdown", reply_markup=keyboard, **kwargs)


def edit_message(message_id, message, keyboard=None, **kwargs):
    return telepot.Bot(TELEGRAM_TOKEN).editMessageText(message_id, message, parse_mode="Markdown", reply_markup=keyboard, **kwargs)


def answer_callback_query(query_id, message='', **kwargs):
    return telepot.Bot(TELEGRAM_TOKEN).answerCallbackQuery(query_id, text=message, **kwargs)


def delete_message(message_id):
    return telepot.Bot(TELEGRAM_TOKEN).deleteMessage(message_id)
