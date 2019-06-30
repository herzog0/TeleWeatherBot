from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from ..database.userDAO import subscribed_coords, has_trigger, has_daily_alert
from ..communication.send_to_user import edit_message, answer_callback_query, inline_keyboard_message


def set_notification_type(message_id, query_id=False):
    choose_type = """Escolha o tipo de notificação que deseja configurar"""

    daily_notf = InlineKeyboardButton(text='Notificação diária',
                                      callback_data='notification.type.daily')

    trigger_notf = InlineKeyboardButton(text='Notificação por gatilho',
                                        callback_data='notification.type.trigger')
    
    unsubs_daily = InlineKeyboardButton(text='*(Descadastrar)*Notificação diária',
                                        callback_data='notification.unsubscribe.daily')
    
    unsubs_trigger = InlineKeyboardButton(text='*(Descadastrar)*Notificação por gatilho',
                                          callback_data='notification.unsubscribe.trigger')
    
    if len(message_id) > 1:
        chat_id = message_id[0]
    else:
        chat_id = message_id
        
    # if has_trigger(chat_id):
    #     trigger_notf = unsubs_trigger
    #
    # if has_daily_alert(chat_id):
    #     daily_notf = unsubs_daily
    #
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[daily_notf], [trigger_notf]])

    if query_id:
        edit_message(message_id, choose_type, keyboard)
        answer_callback_query(query_id)
    else:
        inline_keyboard_message(chat_id, choose_type, keyboard)


def set_notification_location(message_id, by_trigger=False):
    place = subscribed_coords(str(message_id[0]))
#     msg_edit = f"""
# {"*Atenção*: você já possui um alerta por gatilho configurado! Ao cadastrar outro, o primeiro será desconsiderado."
#     if (by_trigger and has_trigger(message_id[0])) else ""}
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
        [InlineKeyboardButton(text='<< Voltar',
                              callback_data='notification.set.go_back')]
    ])

    keyboard_boring = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='<< Voltar',
                              callback_data='notification.set.go_back')]
    ])

    if place:
        edit_message(message_id, msg_edit, keyboard_cool)
    else:
        edit_message(message_id, msg_edit, keyboard_boring)


def set_notification_triggers(message_id):
    msg = """
Agora você precisa escolher a *intenção do gatilho*, ele será relacionado a qual tipo de previsão?
*Atenção*: caso um gatilho seja disparado, você receberá notificações aproximadamente:
- 9 horas antes do evento ocorrer
- 6 horas antes do evento ocorrer
- entre o momento e 3 horas antes do evento ocorrer
"""

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Temperatura',
                              callback_data='notification.set.trig_flavor.temperature')],
        [InlineKeyboardButton(text='Chuva',
                              callback_data='notification.set.trig_flavor.rain')],
        [InlineKeyboardButton(text='Nebulosidade',
                              callback_data='notification.set.trig_flavor.clouds')],
        [InlineKeyboardButton(text='Umidade',
                              callback_data='notification.set.trig_flavor.humidity')],
    ])
    if len(message_id) > 1:
        chat_id = message_id[0]
    else:
        chat_id = message_id
    inline_keyboard_message(chat_id, msg, keyboard)


def set_trigger_condition(message_id, is_rain=False):
    prefix = f"""
Perfeito!
Agora, note que:
"""
    msg = f"""
- As temperaturas serão fornecidas em graus Celsius
- Nebulosidade é informada pela porcentagem de cobertura do céu
- Umidade é informada pela porcentagem de umidade do ar

Baseado nisto, escolha se deseja disparar o gatilho para um valor maior ou menor do que o que você inserir.
"""
    msg_rain = """
- Gatilhos de chuva apenas dizem se haverá chuva ou não, independentemente da intensidade dela

Baseado nisto, escolha se deseja disparar o gatilho quando for ou quando *não* for chover 
"""

    kbd = [
        [InlineKeyboardButton(text='Menor que',
                              callback_data='notification.set.trig_cond.lt')],
        [InlineKeyboardButton(text='Maior que',
                              callback_data='notification.set.trig_cond.gt')]
    ]

    rain_kbd = [
        [InlineKeyboardButton(text='Quando chover',
                              callback_data='notification.set.trig_cond.rain')],
        [InlineKeyboardButton(text='Quando não chover',
                              callback_data='notification.set.trig_cond.not_rain')]
    ]

    if is_rain:
        kbd = rain_kbd
        msg = msg_rain

    msg = prefix + msg

    keyboard = InlineKeyboardMarkup(inline_keyboard=kbd)

    if len(message_id) > 1:
        edit_message(message_id, msg, keyboard)
    else:
        chat_id = message_id
        inline_keyboard_message(chat_id, msg, keyboard)
