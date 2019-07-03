import json
import os
from datetime import datetime

import firebase_admin
import telepot
from firebase_admin import firestore
from pyowm import OWM

owm_token = os.environ.get('OWM_TOKEN', None)

__owm = None

try:
    firebase_admin.initialize_app()
except ValueError:
    pass


def respond(err, res=None):
    response = {
        "statusCode": 400 if err else 200,
        "body": str(err) if err else json.dumps(res),
        "headers": {
            "Content-Type": "application/json",
        },
    }

    return response["body"], response["statusCode"], response["headers"]


def schedular(request=None):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    get_users_with_alerts()
    return respond(None, "ok")


def get_users_with_alerts():

    try:
        __users = firestore.client().collection(u'users').stream()

        global __owm
        if not __owm:
            __owm = OWM(
                API_key=owm_token,
                # config_module='configuration'
                # essa configuração acima muda a linguagem para 'pt' e
                # adiciona um cache simples pra tentar reduzir os requests
            )

        for user in __users:
            chat_id = user.id
            user = user.to_dict()
            user_alert = user.get("ALERT", None)
            if user_alert:
                if "DAILY" in user_alert:
                    hour = user_alert["DAILY"]
                    if (hour+3) % 24 == datetime.utcnow().hour:
                        forecast_info = get_forecast_info("all", user["NOTIFICATION_COORDS"])
                        send_message(chat_id, forecast_info)
                if "TRIGGER" in user_alert:
                    # user_alert["TRIGGER"] deve ser um dicionário contendo o pedido de trigger, uma chave para:
                    # saber se a pessoa quer o gatilho para um valor menor ou maior que o estipulado
                    # o valor estipulado
                    # formato: {"FLAVOR": "temp/cloud/humid", "less_than": int/float / "greater_than": int/float}
                    #          {"FLAVOR": "rain", "cond": "true"/"false"}
                    if datetime.now().hour % 3 == 0:
                        forecast_info = get_forecast_info(user_alert["TRIGGER"], user["NOTIFICATION_COORDS"])
                        if forecast_info:
                            send_message(chat_id, forecast_info)
    except KeyError:
        return None


def get_forecast_info(key, coords):
    fc = __owm.three_hours_forecast_at_coords(coords['lat'], coords['lng'])
    fc = fc.get_forecast().get_weathers()[:8]

    if key == "all":

        data_min, m_time, data_max, mx_time = find_range(fc, "temperature")
        info = f"Temperatura *mínima* de {data_min:.1f}°C às {m_time.hour}h e *máxima* de {data_max:.1f}°C às {mx_time.hour}h\n"
        temp_now = __owm.weather_at_coords(coords['lat'], coords['lng']).get_weather().get_temperature('celsius')[
            "temp"]
        info += f"Temperatura *agora* {temp_now:.1f}°C\n"

        data_min, m_time, data_max, mx_time = find_range(fc, "clouds")
        info += f"Cobertura *mínima* do céu por nuvens de {data_min}% às {m_time.hour}h e *máxima* de {data_max}% às {mx_time.hour}h\n"

        data_min, m_time, data_max, mx_time = find_range(fc, "humidity")
        info += f"Umidade *mínima* de {data_min}% às {m_time.hour}h e *máxima* de {data_max}% às {mx_time.hour}h\n"

        rain, rm_time = find_range(fc, "rain")
        info += f'{f"Terá *chuva* às {rm_time.hour}" if rain else "Não choverá hoje"}'

        return info

    elif isinstance(key, dict):

        fc = fc[:2]

        triggered = False
        info = "*Notificação de alerta*\n*Sua configuração*: "

        flavor = key.get("FLAVOR", None)

        if key.get("CONDITION", None) == 'lt':
            lt = True
            gt = False
        else:
            gt = True
            lt = False

        value = key.get("VALUE", None)
        value = int(value)

        if flavor == "temperature":
            data_min, m_time, data_max, mx_time = find_range(fc, "temperature")
            if lt and value >= data_min:
                triggered = True
                info += f"avisar quando a temperatura for ficar abaixo de {value:.1f}°C\n"
                info += f"A temperatura será de *{data_min:.1f}°C* às *{m_time.hour}h*"
            elif gt and value <= data_max:
                triggered = True
                info += f"avisar quando a temperatura for ficar acima de {value:.1f}°C\n"
                info += f"A temperatura será de *{data_max:.1f}°C* às *{mx_time.hour}h*"

        elif flavor == "clouds":
            data_min, m_time, data_max, mx_time = find_range(fc, "clouds")
            if lt and value >= data_min:
                triggered = True
                info += f"avisar quando a cobertura do céu for ficar abaixo de {value:.1f}%\n"
                info += f"O céu ficará *{data_min:.0f}%* coberto às *{m_time.hour}h*"
            elif gt and value <= data_max:
                triggered = True
                info += f"avisar quando a cobertura do céu for ficar acima de {value:.1f}%\n"
                info += f"O céu ficará *{data_max:.0f}%* coberto às *{mx_time.hour}h*"

        elif flavor == "humidity":
            data_min, m_time, data_max, mx_time = find_range(fc, "humidity")
            if lt and value >= data_min:
                triggered = True
                info += f"avisar quando a umidade do ar for ficar abaixo de {value:.1f}%\n"
                info += f"A umidade será de *{data_min:.0f}%* às *{m_time.hour}h*"
            elif gt and value <= data_max:
                triggered = True
                info += f"avisar quando a umidade do ar for ficar acima de {value:.1f}%\n"
                info += f"A umidade será de *{data_max:.0f}%* às *{mx_time.hour}h*"

        elif flavor == "rain":
            rain, rm_time = find_range(fc, "rain")
            cond = key.get("CONDITION", None)
            if rain and cond and cond == "rain":
                triggered = True
                info += f"avisar se irá chover\n"
                info += f"Terá *chuva* às {rm_time.hour}"
            elif not rain and cond and cond == "not_rain":
                triggered = True
                info += f"avisar se *não* irá chover\n"
                info += f"Não choverá nas próximas horas"

        if triggered:
            return info


def find_range(fc, key):
    fc_min = None
    fc_max = None
    date_min = None
    date_max = None
    for f in fc:
        if key == "temperature":
            ref = f.get_temperature('celsius')
            if fc_min is None or fc_min > ref["temp_min"]:
                fc_min = ref["temp_min"]
                date_min = datetime.fromtimestamp(f.get_reference_time())
            if fc_max is None or fc_max < ref["temp_max"]:
                fc_max = ref["temp_max"]
                date_max = datetime.fromtimestamp(f.get_reference_time())

        elif key == "clouds":
            ref = f.get_clouds()
            if fc_min is None or fc_min > ref:
                fc_min = ref
                date_min = datetime.fromtimestamp(f.get_reference_time())
            if fc_max is None or fc_max < ref:
                fc_max = ref
                date_max = datetime.fromtimestamp(f.get_reference_time())

        elif key == "humidity":
            ref = f.get_humidity()
            if fc_min is None or fc_min > ref:
                fc_min = ref
                date_min = datetime.fromtimestamp(f.get_reference_time())
            if fc_max is None or fc_max < ref:
                fc_max = ref
                date_max = datetime.fromtimestamp(f.get_reference_time())

        elif key == "rain":
            ref = f.get_status().lower()
            if ref == "rain":
                return True, datetime.fromtimestamp(f.get_reference_time())

    if key == "rain":
        return False, datetime.now()

    return fc_min, date_min, fc_max, date_max


def send_message(chat_id, message):
    bot = telepot.Bot(os.environ.get('TELEGRAM_TOKEN', None))
    return bot.sendMessage(chat_id, message, parse_mode="Markdown")
