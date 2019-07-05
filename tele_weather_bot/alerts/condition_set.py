from tele_weather_bot.database.userDAO import update, remove_key
from tele_weather_bot.database.user_keys import UserDataKeys
from tele_weather_bot.communication.send_to_user import markdown_message
from tele_weather_bot.google_maps.geocode_functions import LocationNotFoundException, get_user_address_by_name


def set_not_rain_trigger(chat_id, text, flavor):
    temp = (flavor == 'temp')
    try:
        if not temp:
            text = text.split('%')[0]
        value = int(text)
    except ValueError:
        raise ValueError(f"{'Envie um valor entre -20 e 50 para temperatura' if temp else 'Envie um valor entre 0 e 100 para porcentagens'}")

    if not temp:
        if not 0 <= value <= 100:
            raise ValueError('Envie um valor entre 0 e 100 para porcentagens')
        if flavor == 'clouds':
            update(chat_id, {UserDataKeys.WEATHER_ALERT_VALUE: str(value)})
            markdown_message(chat_id, f"Gatilho configurado para {value}%")
            remove_key(chat_id, UserDataKeys.STATE)
        elif flavor == 'humid':
            update(chat_id, {UserDataKeys.WEATHER_ALERT_VALUE: str(value)})
            markdown_message(chat_id, f"Gatilho configurado para {value}%")
            remove_key(chat_id, UserDataKeys.STATE)
    else:
        if not -20 <= value <= 50:
            raise ValueError('Envie um valor entre -20 e 50 para temperatura')
        update(chat_id, {UserDataKeys.WEATHER_ALERT_VALUE: str(value)})
        markdown_message(chat_id, f"Gatilho configurado para {value}°C")
        remove_key(chat_id, UserDataKeys.STATE)


def set_daily_alert_time(chat_id, text):
    try:
        text = text.split('h')[0]
        hour = int(text)
        if not 0 <= hour <= 23:
            raise ValueError
    except ValueError:
        raise ValueError("Você deve inserir um horário como um número entre 0h e 23h.")

    update(chat_id, {UserDataKeys.WEATHER_DAILY_ALERT: hour})
    remove_key(chat_id, UserDataKeys.STATE)
    markdown_message(chat_id, f"*Alerta diário configurado*: você receberá todo dia, às {hour}h, um resumo das 24h "
                              f"seguintes")


def set_alert_location(chat_id, location):
    """
    :param chat_id: the chat_id talking to the bot
    :param location: the location sent, may be a dictionary with 'lat' and 'lng' keys or a string
    :return: None

    This method's ethos is to ensure that the user sends a valid location to the alerts subscribing system.

    """
    try:
        address, coords = get_user_address_by_name(location)
        update(chat_id, {UserDataKeys.NOTIFICATION_COORDS: coords})
        markdown_message(chat_id, f"""
Certo, o local configurado para receber notificações é:
*{address}*
""")
        return True
    except LocationNotFoundException:
        markdown_message(chat_id, "Insira um local válido")
        return False
