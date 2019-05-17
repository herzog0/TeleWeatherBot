from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from ..database.userDAO import subscribed_coords


class Notification:

    @staticmethod
    def set_notification_type(bot, message_id, query_id=False):

        choose_type = """Escolha o tipo de notificação que deseja configurar"""

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Notificação diária', callback_data='notification.type.daily')],
            [InlineKeyboardButton(text='Notificação por gatilho', callback_data='notification.type.trigger')]
        ])

        if query_id:
            bot.edit_message(message_id, choose_type, keyboard)
            bot.answer_callback_query(query_id)
        else:
            if len(message_id) > 1:
                chat_id = message_id[0]
            else:
                chat_id = message_id
            bot.inline_keyboard_message(chat_id, choose_type, keyboard)

    @staticmethod
    def set_notification_location(bot, message_id, by_trigger=False):
        place = subscribed_coords(str(message_id[0]))
        msg_edit = f"""
*Certo!*
Você escolheu receber notificações {'por gatilho' if by_trigger else 'diárias'} sobre o clima de *algum* local.
Nos diga uma localização sobre a qual você deseja receber notícias.
*Envie o nome de um lugar ou a sua localização atual{' ou, se preferir, toque no botão para usar o '
                                                     'seu local já cadastrado.' if place else ''}*
(Note que a localização cadastrada não será atualizada caso você mude de lugar)
        """
        keyboard_cool = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Usar local já cadastrado',
                                  callback_data='notification.set.use_subscribed_place')],
            [InlineKeyboardButton(text='<< Voltar', callback_data='notification.set.go_back')]
        ])

        keyboard_boring = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='<< Voltar', callback_data='notification.set.go_back')]
        ])

        if place:
            bot.edit_message(message_id, msg_edit, keyboard_cool)
        else:
            bot.edit_message(message_id, msg_edit, keyboard_boring)


    @staticmethod
    def set_notification_hour():
        msg_edit = """"""
        pass
