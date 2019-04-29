from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton


class Notification:

    @staticmethod
    def set_notification_type(bot_instance, chat_id):

        choose_type = """Escolha o tipo de notificação que deseja configurar"""

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Notificação diária', callback_data='daily')],
            [InlineKeyboardButton(text='Notificação por gatilho', callback_data='trigger')]
        ])

        bot_instance.simple_message(chat_id, "blalbalf odase")
        bot_instance.inline_keyboard_message(chat_id, choose_type, keyboard)


