"""
O bot propriamente
"""
import telepot

from datetime import datetime, timedelta
from pyowm.exceptions.api_call_error import APICallError

from tele_weather_bot.alerts.condition_set import set_not_rain_trigger, set_daily_alert_time, set_alert_location
from tele_weather_bot.trivials.trivial_commands import call_help, start
from .weather import NotFoundError
from .weather.api import get_rain, get_weather_description, get_temperature, get_humidity, \
    get_clouds, get_sunrise, get_sunset
from .parser import parser, CouldNotUnderstandException, MoreThanFiveDaysException
from .alerts.keyboards import set_notification_type, set_notification_location, set_trigger_condition, \
    set_notification_triggers
from .google_maps.geocode_functions import LocationNotFoundException, get_user_address_by_name
from .database.user_keys import UserStateKeys, UserDataKeys
from .database.userDAO import update, state, remove_key, name, email, subscribed_coords, last_update, trigger_flavor, \
    has_alerts, delete_user

from .communication.send_to_user import markdown_message, answer_callback_query


def receiver(data):
    """Receives data from Lambda
    """

    # Handlers
    update_types = {
        'message': on_chat_message,
        # 'edited_message': _edited_message,
        # 'channel_post': _channel_post,
        # 'edited_channel_post': _edited_channel_post,
        # 'inline_query': _inline_query,
        # 'chosen_inline_result': _chosen_inline_result,
        'callback_query': on_callback_query
    }

    update_type = 0

    # Get update info
    for key in data:
        if key == 'update_id':
            pass
        else:
            update_type = key

    # Call correct handler passing correct values
    return update_types[update_type](data[update_type])


def on_chat_message(msg):

    content_type, _, chat_id, _, message_id = telepot.glance(msg, long=True)
    # - long: (content_type, msg["chat"]["type"], msg["chat"]["id"], msg["date"], msg["message_id"])
    chat_id = str(chat_id)

    l_upd = last_update(chat_id)
    # apagar estados do usuário se ele ficou inativo por mais de 3 minutos
    if state(chat_id):
        if l_upd and datetime.now() - datetime.fromtimestamp(float(l_upd)) >= timedelta(seconds=180):
            remove_key(chat_id, UserDataKeys.STATE)
            markdown_message(chat_id, "*Cadastro de informações ou de alerta interrompido, tempo limite de 3 minutos "
                                      "excedido*")

    response = None

    # If the message is a text message
    if content_type == 'text':
        response = evaluate_text(msg["text"], chat_id, message_id)

    elif content_type == 'location':
        response = evaluate_location(msg)

    if isinstance(response, str):
        markdown_message(chat_id, response)


def evaluate_location(msg):
    chat_id, message_id = get_message_id(msg)
    return evaluate_text(str(msg["location"]["latitude"]) + " " + str(msg["location"]["longitude"]), chat_id, message_id)


def evaluate_text(text: str, chat_id: str, message_id: int):

    try:
        qtype, location = parser.parse(chat_id, text)

        if not location:
            not_weather_rqst(text, chat_id, message_id, qtype)
        else:
            weather_rqst(chat_id, qtype, location)
    except APICallError:
        return '*Parece que a base de dados de tempo está offline, tente novamente em algum tempo*'
    except MoreThanFiveDaysException as e:
        return f'{str(e)}'
    except AssertionError:
        return '*Infelizmente não entendi o que você falou :(*'
    except CouldNotUnderstandException as e:
        return f'{str(e)}'
    except ValueError as e:
        return f'{str(e)}'
    except NotFoundError:
        return '*Infelizmente não entendi o que você falou :(*'
    except LocationNotFoundException as e:
        return str(e)


def not_weather_rqst(text: str, chat_id: str, message_id: int, qtype):
    def set_subscription():
        evaluate_subscription(chat_id, text)

    def subscribing_daily_alert_place():
        if set_alert_location(chat_id, text):
            update(chat_id, {UserDataKeys.STATE: UserStateKeys.EXPECTING_DAILY_HOUR})
            markdown_message(chat_id, "Agora, envie o horário em que deseja receber as notificações diariamente")

    def subscribing_trigger_alert_place():
        if set_alert_location(chat_id, text):
            remove_key(chat_id, UserDataKeys.STATE)
            set_notification_triggers((chat_id, message_id))

    def expecting_trigger_temperature():
        set_not_rain_trigger(chat_id, text, flavor="temp")

    def expecting_trigger_clouds():
        set_not_rain_trigger(chat_id, text, flavor="clouds")

    def expecting_trigger_humid():
        set_not_rain_trigger(chat_id, text, flavor="humid")

    def expecting_daily_hour():
        set_daily_alert_time(chat_id, text)

    def initial_message():
        start(chat_id)

    def help_request():
        call_help(chat_id, text)

    def set_alarm():
        set_notification_type((chat_id, message_id))

    def cancel():
        remove_key(chat_id, UserDataKeys.STATE) and markdown_message(chat_id, "*Processo cancelado*")

    def erase_subscription():
        msg = "Suas informações foram apagadas!" if delete_user(chat_id) else "Não há nada para apagar!"
        markdown_message(chat_id, msg)

    key_fn = {
        'SET_SUBSCRIPTION': set_subscription,
        'SUBSCRIBING_NAME': set_subscription,
        'SUBSCRIBING_EMAIL': set_subscription,
        'SUBSCRIBING_PLACE': set_subscription,
        'SUBSCRIBING_DAILY_ALERT_PLACE': subscribing_daily_alert_place,
        'SUBSCRIBING_TRIGGER_ALERT_PLACE': subscribing_trigger_alert_place,
        'EXPECTING_TRIGGER_TEMPERATURE': expecting_trigger_temperature,
        'EXPECTING_TRIGGER_CLOUDS': expecting_trigger_clouds,
        'EXPECTING_TRIGGER_HUMID': expecting_trigger_humid,
        'EXPECTING_DAILY_HOUR': expecting_daily_hour,
        'INITIAL_MESSAGE': initial_message,
        'HELP_REQUEST': help_request,
        'SET_ALARM': set_alarm,
        'CANCEL': cancel,
        'ERASE_SUBS': erase_subscription
    }
    key_fn[qtype.name]()


def weather_rqst(chat_id: str, qtype, location):
    full_adress = location[0]
    coords = location[1]
    pairs = qtype

    def weather_fn():
        weather = get_weather_description(coords, tag_date)
        temp = get_temperature(coords, tag_date)

        return f'{weather.capitalize()}\n' \
            f'Temperatura no horário pedido: {temp:.1f}°C'

    def temperature():
        temp = get_temperature(coords, tag_date)
        return f'Temperatura no horário pedido: {temp:.1f}°C'

    def humidity_fn():
        humidity = get_humidity(coords, tag_date)
        return f'Lá o ar está com {humidity}% de umidade'

    def rain():
        rainy = get_rain(coords, tag_date)
        return f'{"Com" if rainy else "Sem"} chuva para este horário'

    def sky_coverage():
        cloudiness = get_clouds(coords, tag_date)
        if 0 <= cloudiness <= 10:
            return "Céu limpo"
        elif 10 < cloudiness <= 30:
            return "Céu predominantemente limpo"
        elif 30 < cloudiness <= 60:
            return "Céu parcialmente nublado"
        elif 60 < cloudiness <= 90:
            return "Céu predominantemente nublado"
        elif 90 < cloudiness <= 100:
            return "Céu nublado"

    def sunrise():
        hour, minute, second = get_sunrise(coords)
        return f'O sol irá nascer às *{hour}h{minute}min{second}s* do horário de Brasília'

    def sunset():
        hour, minute, second = get_sunset(coords)
        return f'O sol irá se pôr às *{hour}h{minute}min{second}s* do horário de Brasília'

    key_weather_fn = {
        'WEATHER': weather_fn,
        'TEMPERATURE': temperature,
        'HUMIDITY': humidity_fn,
        'RAIN': rain,
        'SKY_COVERAGE': sky_coverage,
        'SUNRISE': sunrise,
        'SUNSET': sunset
    }

    assert pairs

    markdown_message(chat_id, "*Certo, encontrei este endereço:*")
    markdown_message(chat_id, full_adress)

    for pair in pairs:
        tag = pair[0]
        tag_date = pair[1]
        response = f'{date_string(tag_date)}'
        response += key_weather_fn[tag.name]()
        markdown_message(chat_id, response)


def on_callback_query(callback_query):
    query_id, from_id, query_data = telepot.glance(callback_query, flavor='callback_query')

    # Build message identification
    message_id = get_message_id(callback_query)
    chat_id = str(message_id[0])

    query_id = str(query_id)

    def not_type():
        query_dt = query_data.split('.')
        key_state_types = {
            'daily': UserStateKeys.SUBSCRIBING_DAILY_ALERT_PLACE,
            'trigger': UserStateKeys.SUBSCRIBING_TRIGGER_ALERT_PLACE
        }
        update(chat_id, {UserDataKeys.STATE: key_state_types[query_dt[-1]]})
        if query_dt[-1] == 'daily':
            set_notification_location(message_id, query_id)
        else:
            set_notification_location(message_id, query_id, by_trigger=True)

    def not_unsubs():
        query_dt = query_data.split('.')
        alert_keys = {
            'daily': UserDataKeys.WEATHER_DAILY_ALERT,
            'trigger': UserDataKeys.WEATHER_TRIGGER_ALERT
        }
        remove_key(chat_id, alert_keys[query_dt[-1]])
        if not has_alerts(chat_id):
            remove_key(chat_id, UserDataKeys.ALERT)
            remove_key(chat_id, UserDataKeys.NOTIFICATION_COORDS)
        if query_dt[-1] == 'daily':
            set_notification_type(message_id, query_id, un_daily=True)
        else:
            set_notification_type(message_id, query_id, un_trig=True)

    def not_set_usesubsplace():
        set_alert_location(chat_id, subscribed_coords(chat_id))
        if state(chat_id) is UserStateKeys.SUBSCRIBING_DAILY_ALERT_PLACE:
            update(chat_id, {UserDataKeys.STATE: UserStateKeys.EXPECTING_DAILY_HOUR})
            markdown_message(chat_id, "Agora, envie o horário em que deseja receber as notificações "
                                      "diariamente")
        else:
            remove_key(chat_id, UserDataKeys.STATE)
            set_notification_triggers(message_id, query_id)
        answer_callback_query(query_id)

    def not_set_goback():
        remove_key(chat_id, UserDataKeys.STATE)
        set_notification_type(message_id, query_id)

    def not_set_trigflavor():
        query_dt = query_data.split('.')
        update(chat_id, {UserDataKeys.WEATHER_ALERT_FLAVOR: query_dt[-1]})
        if query_dt[-1] == 'rain':
            set_trigger_condition(message_id, query_id, is_rain=True)
        else:
            set_trigger_condition(message_id, query_id)

    def not_set_trigcond():
        query_dt = query_data.split('.')
        key_state_flavors = {
            'temperature': UserStateKeys.EXPECTING_TRIGGER_TEMPERATURE,
            'clouds': UserStateKeys.EXPECTING_TRIGGER_CLOUDS,
            'humidity': UserStateKeys.EXPECTING_TRIGGER_HUMID,
        }
        flavor = trigger_flavor(chat_id)
        update(chat_id, {UserDataKeys.STATE: key_state_flavors[flavor],
                         UserDataKeys.WEATHER_ALERT_COND: query_dt[-1]})
        msg = "Envie um valor entre 0 e 100 para porcentagens"
        if flavor == 'temperature':
            msg = "Envie um valor entre -20 e 50 para temperatura"
        answer_callback_query(query_id)
        markdown_message(chat_id, msg)

    def not_set_trigcond_rain():
        query_dt = query_data.split('.')
        cond = query_dt[-1]
        bool_rain = cond == 'rain'
        update(chat_id, {UserDataKeys.WEATHER_ALERT_COND: cond})
        remove_key(chat_id, UserDataKeys.WEATHER_ALERT_VALUE)
        markdown_message(chat_id, f"Gatilho configurado, você saberá quando{'*não*' if not bool_rain else ''} for chover")
        answer_callback_query(query_id)

    not_fn = {
        'notification.type.daily': not_type,
        'notification.type.trigger': not_type,
        'notification.unsubscribe.daily': not_unsubs,
        'notification.unsubscribe.trigger': not_unsubs,
        'notification.set.use_subscribed_place': not_set_usesubsplace,
        'notification.set.go_back': not_set_goback,
        'notification.set.trig_flavor.temperature': not_set_trigflavor,
        'notification.set.trig_flavor.rain': not_set_trigflavor,
        'notification.set.trig_flavor.clouds': not_set_trigflavor,
        'notification.set.trig_flavor.humidity': not_set_trigflavor,
        'notification.set.trig_cond.lt': not_set_trigcond,
        'notification.set.trig_cond.gt': not_set_trigcond,
        'notification.set.trig_cond.rain': not_set_trigcond_rain,
        'notification.set.trig_cond.not_rain': not_set_trigcond_rain,
    }

    not_fn[query_data]()


def get_message_id(msg):
    try:
        return telepot.message_identifier(msg)
    except ValueError:
        return msg["message"]["chat"]["id"], msg["message"]["message_id"]


def date_string(date: datetime):
    return str(f'{date.day}/{date.month}/{date.year} às {(date.hour-3)%24}h'
               f'\n*----------------------*\n')


def evaluate_subscription(chat_id, text):
    if not state(chat_id):
        update(chat_id, {UserDataKeys.STATE: UserStateKeys.SUBSCRIBING_NAME})
        markdown_message(chat_id, '*Qual seu nome?*')

    elif state(chat_id) is UserStateKeys.SUBSCRIBING_NAME:
        update(chat_id, {UserDataKeys.NAME: text})
        update(chat_id, {UserDataKeys.STATE: UserStateKeys.SUBSCRIBING_EMAIL})
        markdown_message(chat_id, '*Qual seu e-mail?*')

    elif state(chat_id) is UserStateKeys.SUBSCRIBING_EMAIL:
        update(chat_id, {UserDataKeys.EMAIL: text})
        update(chat_id, {UserDataKeys.STATE: UserStateKeys.SUBSCRIBING_PLACE})
        markdown_message(chat_id, '*Qual o seu lugar de cadastro?*\n(Envie um nome ou uma localização')

    elif state(chat_id) is UserStateKeys.SUBSCRIBING_PLACE:
        address = None
        try:
            address, coords = get_user_address_by_name(text)
            update(chat_id, {UserDataKeys.SUBSCRIBED_COORDS: coords})
        except LocationNotFoundException as e:
            remove_key(chat_id, UserDataKeys.SUBSCRIBED_COORDS)
            markdown_message(chat_id, f'*{str(e)}*')
        remove_key(chat_id, UserDataKeys.STATE)
        markdown_message(chat_id, f"""
*Parabéns!*
*Agora você possui funcionalidade especiais.*

Você inseriu as informações:
*Nome*: {name(chat_id)}
*Email*: {email(chat_id)}
*Localização*: {address or 'Local não informado'}

Caso queira alterar os dados basta recomeçar o cadastro.
Digite "*ajuda cadastro*" para obter mais informações sobre as funcionalidades especiais.

""")
