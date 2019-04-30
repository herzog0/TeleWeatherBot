from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton


class Notification:

    @staticmethod
    def set_notification_type(bot_instance, message_id, query_id=False):

        choose_type = """Escolha o tipo de notificação que deseja configurar"""

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Notificação diária', callback_data='notification.type.daily')],
            [InlineKeyboardButton(text='Notificação por gatilho', callback_data='notification.type.trigger')]
        ])

        if query_id:
            bot_instance.edit_message(message_id, choose_type, keyboard)
            bot_instance.answer_callback_query(query_id)
        else:
            if len(message_id) > 1:
                chat_id = message_id[0]
            else:
                chat_id = message_id
            bot_instance.inline_keyboard_message(chat_id, choose_type, keyboard)

    @staticmethod
    def set_daily_notification(bot_instance, message_id):
        msg_edit = """
*Certo!*
Você escolheu receber notificações diárias sobre o clima de *algum* local.
Nos diga uma localização sobre a qual você deseja receber notícias escolhendo uma opção abaixo.
*(Note que a localização cadastrada não será atualizada caso você mude de lugar)*
        """

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Localização atual', callback_data='notification.set.location')],
            [InlineKeyboardButton(text='Diga uma cidade', callback_data='notification.set.city')],
            [InlineKeyboardButton(text='<< Voltar', callback_data='notification.set.goback')]
        ])

        bot_instance.edit_message(message_id, msg_edit, keyboard)

    @staticmethod
    def set_notification_by_trigger(bot_instance, message_id):
        pass

    @staticmethod
    def set_daily_location(bot_instance, message_id):
        pass

    @staticmethod
    def set_daily_city(bot_instance, message_id):
        pass
