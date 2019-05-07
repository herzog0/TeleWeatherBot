from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


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
            [InlineKeyboardButton(text='<< Voltar', callback_data='notification.set.go_back')]
        ])

        bot_instance.edit_message(message_id, msg_edit, keyboard)

    @staticmethod
    def set_daily_notification_by_location(bot_instance, message_id):
        message = """..."""
        keyboard = ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text='Enviar localização', request_location=True)]
            ],
            resize_keyboard=True,
            one_time_keyboard=True
        )

        keyboard_2 = InlineKeyboardMarkup(inline_keyboard=[
         [InlineKeyboardButton(text='<< Voltar', callback_data='notification.get.cancel.by_location')]
        ])

        chat_id = message_id[0]

        # Envia um botão que aparece no campo de digitação
        msg_kbd_location = bot_instance.markdown_message(chat_id=chat_id, message=message, reply_markup=keyboard)

        # Edita o teclado de seleção de "notificação por cidade ou por localização"
        bot_instance.edit_message(message_id, message="*Aguardando seu envio de localização...*", keyboard=keyboard_2)

        bot_instance.delete_message(bot_instance.get_message_id(msg_kbd_location))

    @staticmethod
    def set_daily_notification_by_city(bot_instance, message_id):
        msg_edit = """Envie o nome da cidade para a qual deseja receber notificações"""

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='<< Voltar', callback_data='notification.get.cancel.by_city')]
        ])

        bot_instance.edit_message(message_id, msg_edit, keyboard)
        pass

    @staticmethod
    def set_notification_by_trigger(bot_instance, message_id):
        pass


