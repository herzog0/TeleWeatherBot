"""
O bot propriamente
"""
import telepot

from datetime import datetime, timedelta
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from pyowm.exceptions.api_call_error import APICallError


from .weather import NotFoundError
from .weather.api import get_rain, get_weather_description, get_temperature, get_humidity, \
    get_clouds, get_sunrise, get_sunset
from .parser import parser, WeatherTypes, FunctionalTypes, CouldNotUnderstandException, MoreThanFiveDaysException
from .alerts.notification import set_notification_type, set_notification_location, set_trigger_condition, \
    set_notification_triggers
from .google_maps.geocode_functions import LocationNotFoundException, get_user_address_by_name
from .database.user_keys import UserStateKeys, UserDataKeys
from .database.userDAO import update, state, remove_key, name, email, subscribed_coords, last_update, trigger_flavor, \
    has_alerts

from .communication.send_to_user import markdown_message, delete_message, simple_message, answer_callback_query


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


def evaluate_text(text: str, chat_id: str, message_id: int):

    try:
        qtype, location = parser.parse(chat_id, text)

        if not location:

            if qtype is FunctionalTypes.SET_SUBSCRIPTION or isinstance(qtype, UserStateKeys):
                if qtype is UserStateKeys.SUBSCRIBING_DAILY_ALERT_PLACE:
                    if set_alert_location(chat_id, text):
                        update(chat_id, {UserDataKeys.STATE: UserStateKeys.EXPECTING_DAILY_HOUR})
                        markdown_message(chat_id, "Agora, envie o horário em que deseja receber as notificações "
                                                  "diariamente")
                elif qtype is UserStateKeys.SUBSCRIBING_TRIGGER_ALERT_PLACE:
                    if set_alert_location(chat_id, text):
                        remove_key(chat_id, UserDataKeys.STATE)
                        set_notification_triggers((chat_id, message_id))
                elif qtype is UserStateKeys.EXPECTING_TRIGGER_TEMPERATURE:
                    set_not_rain_trigger(chat_id, text, flavor='temp')
                elif qtype is UserStateKeys.EXPECTING_TRIGGER_CLOUDS:
                    set_not_rain_trigger(chat_id, text, flavor='clouds')
                elif qtype is UserStateKeys.EXPECTING_TRIGGER_HUMID:
                    set_not_rain_trigger(chat_id, text, flavor='humid')
                elif qtype is UserStateKeys.EXPECTING_DAILY_HOUR:
                    set_daily_alert_time(chat_id, text)
                else:
                    evaluate_subscription(chat_id, text)

            elif qtype is FunctionalTypes.INITIAL_MESSAGE:
                #
                start(chat_id)

            elif qtype is FunctionalTypes.HELP_REQUEST:
                #
                call_help(chat_id, text)

            elif qtype is FunctionalTypes.SET_ALARM:
                set_notification_type((chat_id, message_id))

            elif qtype is FunctionalTypes.CANCEL:
                if remove_key(chat_id, UserDataKeys.STATE):
                    markdown_message(chat_id, "*Processo cancelado*")

        else:

            full_adress = location[0]
            coords = location[1]
            pairs = qtype

            if pairs:
                markdown_message(chat_id, "*Certo, encontrei este endereço:*")
                markdown_message(chat_id, full_adress)
            else:
                raise NotFoundError("Nenhuma interpretação pôde ser feita")

            for pair in pairs:
                tag = pair[0]
                tag_date = pair[1]
                response = f'{date_string(tag_date)}'

                if tag is WeatherTypes.WEATHER:
                    weather = get_weather_description(coords, tag_date)
                    temp = get_temperature(coords, tag_date)

                    response += f'{weather.capitalize()}\n' \
                        f'Temperatura no horário pedido: {temp:.1f}°C'

                elif tag is WeatherTypes.TEMPERATURE:
                    temp = get_temperature(coords, tag_date)
                    response += f'Temperatura no horário pedido: {temp:.1f}°C'

                elif tag is WeatherTypes.HUMIDITY:
                    humidity = get_humidity(coords, tag_date)
                    response += f'Lá o ar está com {humidity}% de umidade'

                elif tag is WeatherTypes.IS_RAINY:
                    rainy = get_rain(coords, tag_date)
                    response += f'{"Com" if rainy else "Sem"} chuva para este horário'

                elif tag is WeatherTypes.SKY_COVERAGE:
                    cloudiness = get_clouds(coords, tag_date)
                    if 0 <= cloudiness <= 10:
                        response += "Céu limpo"
                    elif 10 < cloudiness <= 30:
                        response += "Céu predominantemente limpo"
                    elif 30 < cloudiness <= 60:
                        response += "Céu parcialmente nublado"
                    elif 60 < cloudiness <= 90:
                        response += "Céu predominantemente nublado"
                    elif 90 < cloudiness <= 100:
                        response += "Céu nublado"

                elif tag is WeatherTypes.SUNRISE:
                    hour, minute, second = get_sunrise(coords)
                    response += f'O sol irá nascer às *{hour}h{minute}min{second}s* do horário de Brasília'

                elif tag is WeatherTypes.SUNSET:
                    hour, minute, second = get_sunset(coords)
                    response += f'O sol irá se pôr às *{hour}h{minute}min{second}s* do horário de Brasília'
                    
                return response
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
    markdown_message(chat_id, f"*Alerta diário configurado*: você receberá um resumo das 24h seguintes às {hour}h")


def evaluate_location(msg):
    chat_id, message_id = get_message_id(msg)
    coords = {"lat": msg["location"]["latitude"], "lng": msg["location"]["longitude"]}
    chat_id = str(chat_id)

    user_state = state(chat_id)
    response = None

    if user_state is UserStateKeys.SUBSCRIBING_PLACE:
        evaluate_subscription(chat_id, f'{coords["lat"]} {coords["lng"]}')

    elif user_state is UserStateKeys.SUBSCRIBING_TRIGGER_ALERT_PLACE:
        delete_message((chat_id, message_id))
        if set_alert_location(chat_id, f'{coords["lat"]} {coords["lng"]}'):
            remove_key(chat_id, UserDataKeys.STATE)
            set_notification_triggers((chat_id, message_id))
    elif user_state is UserStateKeys.SUBSCRIBING_DAILY_ALERT_PLACE:
        delete_message((chat_id, message_id))
        if set_alert_location(chat_id, f'{coords["lat"]} {coords["lng"]}'):
            update(chat_id, {UserDataKeys.STATE: UserStateKeys.EXPECTING_DAILY_HOUR})
            markdown_message(chat_id, "Agora, envie o horário em que deseja receber as notificações "
                                      "diariamente")

    else:
        response = evaluate_text(str(coords["lat"]) + " " + str(coords["lng"]), chat_id, message_id)

    if response:
        return response


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


def on_callback_query(callback_query):
    query_id, from_id, query_data = telepot.glance(callback_query, flavor='callback_query')

    # Build message identification
    message_id = get_message_id(callback_query)
    chat_id = str(message_id[0])

    query_id = str(query_id)

    # Navigate the callback if it came from the notifications setter
    if query_data.split('.')[0] == 'notification':

        info = query_data.split('.')
        if info[1] == 'type':

            if info[2] == 'daily':
                update(chat_id, {UserDataKeys.STATE: UserStateKeys.SUBSCRIBING_DAILY_ALERT_PLACE})
                set_notification_location(message_id, query_id)

            elif info[2] == 'trigger':
                update(chat_id, {UserDataKeys.STATE: UserStateKeys.SUBSCRIBING_TRIGGER_ALERT_PLACE})
                set_notification_location(message_id, query_id, by_trigger=True)

        elif info[1] == 'unsubscribe':

            if info[2] == 'daily':
                remove_key(chat_id, UserDataKeys.WEATHER_DAILY_ALERT)
                if not has_alerts(chat_id):
                    remove_key(chat_id, UserDataKeys.ALERT)
                    remove_key(chat_id, UserDataKeys.NOTIFICATION_COORDS)
                set_notification_type(message_id, query_id, un_daily=True)

            elif info[2] == 'trigger':
                remove_key(chat_id, UserDataKeys.WEATHER_TRIGGER_ALERT)
                if not has_alerts(chat_id):
                    remove_key(chat_id, UserDataKeys.ALERT)
                    remove_key(chat_id, UserDataKeys.NOTIFICATION_COORDS)
                set_notification_type(message_id, query_id, un_trig=True)

        elif info[1] == 'set':

            if info[2] == 'use_subscribed_place':
                set_alert_location(chat_id, subscribed_coords(chat_id))
                if state(chat_id) is UserStateKeys.SUBSCRIBING_DAILY_ALERT_PLACE:
                    update(chat_id, {UserDataKeys.STATE: UserStateKeys.EXPECTING_DAILY_HOUR})
                    markdown_message(chat_id, "Agora, envie o horário em que deseja receber as notificações "
                                              "diariamente")
                else:
                    remove_key(chat_id, UserDataKeys.STATE)
                    set_notification_triggers(message_id, query_id)
                answer_callback_query(query_id)

            elif info[2] == 'go_back':
                remove_key(chat_id, UserDataKeys.STATE)
                set_notification_type(message_id, query_id)

            elif info[2] == 'trig_flavor':
                if info[3] == 'temperature':
                    update(chat_id, {UserDataKeys.WEATHER_ALERT_FLAVOR: "temperature"})
                    set_trigger_condition(message_id, query_id)
                elif info[3] == 'clouds':
                    update(chat_id, {UserDataKeys.WEATHER_ALERT_FLAVOR: "clouds"})
                    set_trigger_condition(message_id, query_id)
                elif info[3] == 'humidity':
                    update(chat_id, {UserDataKeys.WEATHER_ALERT_FLAVOR: "humidity"})
                    set_trigger_condition(message_id, query_id)
                elif info[3] == 'rain':
                    update(chat_id, {UserDataKeys.WEATHER_ALERT_FLAVOR: "rain"})
                    set_trigger_condition(message_id, query_id, is_rain=True)

            elif info[2] == 'trig_cond':
                flavor = trigger_flavor(chat_id)
                if flavor == 'temperature':
                    if info[3] == 'lt':
                        update(chat_id, {UserDataKeys.STATE: UserStateKeys.EXPECTING_TRIGGER_TEMPERATURE,
                                         UserDataKeys.WEATHER_ALERT_COND: 'lt'})
                    elif info[3] == 'gt':
                        update(chat_id, {UserDataKeys.STATE: UserStateKeys.EXPECTING_TRIGGER_TEMPERATURE,
                                         UserDataKeys.WEATHER_ALERT_COND: 'gt'})
                    markdown_message(chat_id, "Envie um valor entre -20 e 50 para temperatura")

                elif flavor == 'clouds':
                    if info[3] == 'lt':
                        update(chat_id, {UserDataKeys.STATE: UserStateKeys.EXPECTING_TRIGGER_CLOUDS,
                                         UserDataKeys.WEATHER_ALERT_COND: 'lt'})
                    elif info[3] == 'gt':
                        update(chat_id, {UserDataKeys.STATE: UserStateKeys.EXPECTING_TRIGGER_CLOUDS,
                                         UserDataKeys.WEATHER_ALERT_COND: 'gt'})
                    markdown_message(chat_id, "Envie um valor entre 0 e 100 para porcentagens")

                elif flavor == 'humidity':
                    if info[3] == 'lt':
                        update(chat_id, {UserDataKeys.STATE: UserStateKeys.EXPECTING_TRIGGER_HUMID,
                                         UserDataKeys.WEATHER_ALERT_COND: 'lt'})
                    elif info[3] == 'gt':
                        update(chat_id, {UserDataKeys.STATE: UserStateKeys.EXPECTING_TRIGGER_HUMID,
                                         UserDataKeys.WEATHER_ALERT_COND: 'gt'})
                    markdown_message(chat_id, "Envie um valor entre 0 e 100 para porcentagens")

                elif flavor == 'rain':
                    if info[3] == 'rain':
                        update(chat_id, {UserDataKeys.WEATHER_ALERT_COND: 'rain'})
                        remove_key(chat_id, UserDataKeys.WEATHER_ALERT_VALUE)
                        markdown_message(chat_id, "Gatilho configurado, você saberá quando for chover")
                        remove_key(chat_id, UserDataKeys.STATE)
                    elif info[3] == 'not_rain':
                        update(chat_id, {UserDataKeys.WEATHER_ALERT_COND: 'not_rain'})
                        remove_key(chat_id, UserDataKeys.WEATHER_ALERT_VALUE)
                        markdown_message(chat_id, "Gatilho configurado, você saberá quando *não* for chover")
                        remove_key(chat_id, UserDataKeys.STATE)
                answer_callback_query(query_id)


def date_string(date: datetime):
    return str(f'{date.day}/{date.month}/{date.year} às {(date.hour-3)%24}h'
               f'\n*----------------------*\n')


def get_message_id(msg):
    try:
        message_id = telepot.message_identifier(msg)
        message_id[0] = str(message_id[0])
    except ValueError:
        message_id = (str(msg["message"]["chat"]["id"]), msg["message"]["message_id"])

    return message_id


def call_help(chat_id, text):

    args = text.lower().strip().split()

    main_help_message = u"""
Olá, você está usando o bot TeleWeather!
Usando dados abertos da API do OpenWeather, este bot te dá funcionalidades climáticas como:
*1 - Previsão do tempo*
*2 - Inscrição para notificações programadas*
*3 - Ajuda doméstica ao informar se sua roupa pode ser lavada e quando está seca*
*4 - Informações climáticas diversas*
    
Para saber mais sobre alguma funcionalidade peça ajuda!
ex.: *ajuda 1* (isso dará ajuda sobre a previsão do tempo, pois é o item 1)
ou   *help previsao* (o mesmo que "ajuda 1")
"""

    helptype = None

    if args and len(args) > 1 and ('ajuda' in args or 'help' in args):
        for arg in args:
            if arg in ['1', 1, 'previsão', 'previsao', 'tempo', 'prever']:
                helptype = '1'
            elif arg in ['2', 2, 'inscrição', 'inscricao', 'inscriçao', 'inscricão', 'inscrever', 'notificar',
                         'notificação']:
                helptype = '2'
            elif arg in ['3', 3, 'roupa', 'lavar']:
                helptype = '3'
            elif arg in ['4', 4, 'informações', 'informaçoes', 'informacões', 'informacoes', 'info', 'infos']:
                helptype = '4'

    if helptype == '1':
        simple_message(chat_id, 'ajuda pro 1')

    elif helptype == '2':
        simple_message(chat_id, 'ajuda pro 2')

    elif helptype == '3':
        simple_message(chat_id, 'ajuda pro 3')

    elif helptype == '4':
        simple_message(chat_id, 'ajuda pro 4')

    else:
        markdown_message(chat_id, main_help_message)

    # TODO escrever mensagens de ajuda para cada item especificado


def start(chat_id):
    initial_response_text = """
    Olá!!
    Você está iniciando o TeleWeatherBot!! Bem vindo!!
    Use os seguintes comandos para me pedir algo:
    /help - Lista de comandos disponíveis
    /cadastro - Efetuar cadastro para poder aproveitar mais as funcionalidades
    /clima <Cidade> - Falar como está o clima da Cidade no momento
    """

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Iniciar Cadastro', callback_data='cadastro')],
        [InlineKeyboardButton(text='Exibir comandos disponíveis', callback_data='comandos')]
    ])
    simple_message(chat_id, initial_response_text, reply_markup=keyboard)


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
