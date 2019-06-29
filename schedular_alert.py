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
            forecast_info = "ue nao achou nada"
            user = user.to_dict()
            user_alert = user.get("ALERT", None)
            if user_alert:
                if "DAILY" in user_alert:
                    hour = user_alert["DAILY"]
                    if (hour+3) % 24 == datetime.utcnow().hour:
                        forecast_info = get_forecast_info("all", user["notfication_coords"])
                        print(forecast_info + "dentro do daily")
                elif "TRIGGER" in user_alert:
                    # user_alert["TRIGGER"] deve ser um dicionário contendo o pedido de trigger, uma chave para:
                    # saber se a pessoa quer o gatilho para um valor menor ou maior que o estipulado
                    # o valor estipulado
                    forecast_info = get_forecast_info(user_alert["TRIGGER"], user["notfication_coords"])
                send_message(chat_id, forecast_info)
    except KeyError:
        return None


def get_forecast_info(key, coords):

    fc = __owm.three_hours_forecast_at_coords(coords['lat'], coords['lng'])
    fc = fc.get_forecast().get_weathers()[:8]

    obs = __owm.weather_at_coords(coords['lat'], coords['lng']).get_weather()

    temp_min, tm_time, temp_max, tmx_time = find_range(fc, "temperature")
    clouds_min, cm_time, clouds_max, cmx_time = find_range(fc, "clouds")
    humidity_min, hm_time, humidity_max, hmx_time = find_range(fc, "humidity")
    rain, rm_time = find_range(fc, "rain")
    temp_now = obs.get_temperature('celsius')["temp"]

    if key == "all":
        info = f"""
Temperatura *mínima* de {temp_min:.1f}°C às {tm_time.hour}h e *máxima* de {temp_max:.1f}°C às {tmx_time.hour}h
Temperatura *agora* {temp_now:.1f}°C
Cobertura *mínima* do céu por nuvens de {clouds_min}% às {cm_time.hour}h e *máxima* de {clouds_max}% às {cmx_time.hour}h
Umidade *mínima* de {humidity_min}% às {hm_time.hour}h e *máxima* de {humidity_max}% às {hmx_time.hour}h
{f"Terá chuva às {rm_time.hour}" if rain else "Não choverá hoje"}
"""
        return info

    elif isinstance(key, dict):
        pass


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
