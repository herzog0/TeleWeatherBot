from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton


class Notification:

    @staticmethod
    def set_notification_type(bot_instance, chat_id):

        choose_type = """Escolha o tipo de notificação que deseja configurar"""

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Notificação diária', callback_data='cadastro')],
            [InlineKeyboardButton(text='Notificação por gatilho', callback_data='comandos')]
        ])
        bot_instance.sendMessage(chat_id, choose_type, reply_markup=keyboard)
