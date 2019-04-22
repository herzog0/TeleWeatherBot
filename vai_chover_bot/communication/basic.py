from vai_chover_bot.__main__ import bot


def simple_message(chat_id, message, **kwargs):
    bot.sendMessage(chat_id, message, **kwargs)


def markdown_message(chat_id, message, **kwargs):
    simple_message(chat_id, message, parse_mode="Markdown", **kwargs)


def html_message(chat_id, message, **kwargs):
    simple_message(chat_id, message, parse_mode="HTML", **kwargs)


def inline_keyboard_message(chat_id, message, keyboard=None, **kwargs):
    simple_message(chat_id, message, parse_mode="Markdown", reply_markup=keyboard, **kwargs)


def edit_message(message_id, message, keyboard=None, **kwargs):
    bot.editMessageText(message_id, message, parse_mode="Markdown", reply_markup=keyboard, **kwargs)


def answer_callback_query(query_id, message='', **kwargs):
    bot.answerCallbackQuery(query_id, message, **kwargs)
