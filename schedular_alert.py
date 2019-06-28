from datetime import datetime
import telepot
import json
import os

import firebase_admin
from firebase_admin import credentials, firestore
from tele_weather_bot.weather.api import get_temperature, get_sunrise, get_sunset, get_clouds, get_humidity, \
    get_weather_description, get_rain
from tele_weather_bot.parser.question_keys import WeatherTypes

from pyowm import OWM
from pyowm.weatherapi25.weather import Weather
from pyowm.exceptions.api_call_error import APICallError

owm_token = os.environ.get('OWM_TOKEN', None)

__owm = None

FIREBASE_CERTIFICATE = ""

cred = credentials.Certificate(FIREBASE_CERTIFICATE)
firebase_admin.initialize_app(cred)

__users = None
telepot_token = ""


def respond(err, res=None):
    response = {
        "statusCode": 400 if err else 200,
        "body": str(err) if err else json.dumps(res),
        "headers": {
            "Content-Type": "application/json",
        },
    }

    return response["body"], response["statusCode"], response["headers"]


def schedular(request):
    """Responds to any HTTP request.
    Args:
        request (flask.Request): HTTP request object.
    Returns:
        The response text or any set of values that can be turned into a
        Response object using
        `make_response <http://flask.pocoo.org/docs/1.0/api/#flask.Flask.make_response>`.
    """
    request_json = request.get_json()
    if "run_schedule" in request_json and request_json["run_schedule"] == "true":
        telepot.Bot(telepot_token).sendMessage("154885116", f"rodou schedular\n{datetime.now()}")
    return respond(None, "ok")


def get_users_with_alerts():

    alert_trigger_options = {
        "temperature": get_temperature,
        "clouds": get_clouds,
        "humidity": get_humidity,
        "rain": get_rain,
        "sunrise": get_sunrise,
        "sunset": get_sunset
    }


    try:
        global __users
        if not __users:
            __users = firestore.client().collection(u'users').stream()

        for user in __users:
            chat_id = user.id
            forecast_info = ""
            user = user.to_dict()
            user_alert = user.get("ALERT", None)
            if user_alert:
                if "DAILY" in user_alert:
                    hour = user_alert["DAILY"]
                    if hour == datetime.utcnow().hour:
                        forecast_info = get_forecast_info("all", user["subscribed_coords"])
                elif "TRIGGER" in user_alert:
                    forecast_info = get_forecast_info(user_alert["TRIGGER"], user["subscribed_coords"])






        return response
    except KeyError:
        return None


def get_forecast_info(key, coords):
    return ""


def send_message(chat_id, message):
    global __bot
    if not __bot:
        __bot = telepot.Bot(os.environ.get('TELEGRAM_TOKEN', None))
    return __bot.sendMessage(chat_id, message, parse_mode="Markdown")