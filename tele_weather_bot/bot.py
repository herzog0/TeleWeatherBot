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
from .alerts.notification import set_notification_type, set_notification_location
from .google_maps.geocode_functions import LocationNotFoundException, get_user_address_by_name
from .database.user_keys import UserStateKeys, UserDataKeys
from .database.userDAO import update, state, remove_key, name, email, subscribed_coords, last_update

from .communication.send_to_user import markdown_message, delete_message, simple_message


def on_chat_message(msg):

    content_type, _, chat_id, _, message_id = telepot.glance(msg, long=True)
    # - long: (content_type, msg["chat"]["type"], msg["chat"]["id"], msg["date"], msg["message_id"])
    chat_id = str(chat_id)

    # apagar estados do usuário se ele ficou inativo por mais de 1 minuto
    if last_update(chat_id) and \
            datetime.now() - datetime.fromtimestamp(float(last_update(chat_id))) >= timedelta(seconds=60):
        if state(chat_id):
            remove_key(chat_id, UserDataKeys.STATE)
            markdown_message(chat_id, "*Cadastro de informações ou alerta interrompido, tempo limite de 1 minuto "
                                      "excedido*")

    response = None

    # If the message is a text message
    if content_type == 'text':
        response = evaluate_text(msg["text"], chat_id, message_id)

    elif content_type == 'location':
        response = evaluate_location(msg)

    if isinstance(response, str):
        markdown_message(chat_id, response)


def evaluate_text(text: str, chat_id: str, message_id: int):

    try:
        qtype, location = parser.parse(chat_id, text)

        if not location:
            if qtype is FunctionalTypes.SET_SUBSCRIPTION or isinstance(qtype, UserStateKeys):
                if qtype is UserStateKeys.SUBSCRIBING_DAILY_ALERT_PLACE or \
                        qtype is UserStateKeys.SUBSCRIBING_TRIGGER_ALERT_PLACE:
                    set_alert_location(chat_id, text)
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


def evaluate_location(msg):
    chat_id, message_id = get_message_id(msg)
    coords = {"lat": msg["location"]["latitude"], "lng": msg["location"]["longitude"]}
    chat_id = str(chat_id)

    user_state = state(chat_id)
    response = None

    if user_state is UserStateKeys.SUBSCRIBING_PLACE:
        evaluate_subscription(chat_id, f'{coords["lat"]} {coords["lng"]}')

    elif user_state is UserStateKeys.SUBSCRIBING_TRIGGER_ALERT_PLACE or \
            user_state is UserStateKeys.SUBSCRIBING_DAILY_ALERT_PLACE:
        delete_message((chat_id, message_id))
        set_alert_location(chat_id, f'{coords["lat"]} {coords["lng"]}')

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
        update(chat_id, UserDataKeys.NOTIFICATION_COORDS, coords)
        markdown_message(chat_id, f"""
Certo, o local configurado para receber notificações é:
*{address}*
""")
        remove_key(chat_id, UserDataKeys.STATE)
    except LocationNotFoundException:
        markdown_message(chat_id, "Insira um local válido")


def on_callback_query(callback_query):
    print("entering callback query")
    query_id, from_id, query_data = telepot.glance(callback_query, flavor='callback_query')

    # Build message identification
    message_id = get_message_id(callback_query)
    chat_id = str(message_id[0])

    # Navigate the callback if it came from the notifications setter
    if query_data.split('.')[0] == 'notification':

        info = query_data.split('.')
        value = 0
        if info[1] == 'type':

            if info[2] == 'daily':
                update(chat_id, UserDataKeys.STATE, UserStateKeys.SUBSCRIBING_DAILY_ALERT_PLACE)
                update(chat_id, UserDataKeys.ALERT, {"DAILY": 20})
                value = 1

            elif info[2] == 'trigger':
                update(chat_id, UserDataKeys.STATE, UserStateKeys.SUBSCRIBING_TRIGGER_ALERT_PLACE)
                value = 2

        elif info[1] == 'set':

            if info[2] == 'use_subscribed_place':
                set_alert_location(chat_id, subscribed_coords(chat_id))

            elif info[2] == 'go_back':
                remove_key(chat_id, UserDataKeys.STATE)
                value = 5

        if value == 1:
            set_notification_location(message_id)
        elif value == 2:
            set_notification_location(message_id, by_trigger=True)
        elif value == 5:
            set_notification_type(message_id, query_id)


def date_string(date: datetime):
    return str(f'{date.day}/{date.month}/{date.year} às {(date.hour-3)%24}h'
               f'\n*----------------------*\n')


def get_message_id(msg):
    try:
        message_id = telepot.message_identifier(msg)
    except ValueError:
        message_id = (msg["message"]["chat"]["id"], msg["message"]["message_id"])

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
    chat_id = chat_id
    if not state(chat_id):
        update(chat_id, UserDataKeys.STATE, UserStateKeys.SUBSCRIBING_NAME)
        markdown_message(chat_id, '*Qual seu nome?*')

    elif state(chat_id) is UserStateKeys.SUBSCRIBING_NAME:
        update(chat_id, UserDataKeys.NAME, text)
        update(chat_id, UserDataKeys.STATE, UserStateKeys.SUBSCRIBING_EMAIL)
        markdown_message(chat_id, '*Qual seu e-mail?*')

    elif state(chat_id) is UserStateKeys.SUBSCRIBING_EMAIL:
        update(chat_id, UserDataKeys.EMAIL, text)
        update(chat_id, UserDataKeys.STATE, UserStateKeys.SUBSCRIBING_PLACE)
        markdown_message(chat_id, '*Qual o seu lugar de cadastro?*\n(Envie um nome ou uma localização')

    elif state(chat_id) is UserStateKeys.SUBSCRIBING_PLACE:
        address = None
        try:
            address, coords = get_user_address_by_name(text)
            update(chat_id, UserDataKeys.SUBSCRIBED_COORDS, coords)
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
