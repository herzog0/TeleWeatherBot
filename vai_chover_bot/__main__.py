from . import WeatherBot
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("../database/vai-chover-bot-firebase-adminsdk-jqxyn-df2b6d5553.json")
firebase_admin.initialize_app(cred)

db = firestore.client()


## TOKEN DO MarmisTeste
# telegram_token = '822196045:AAFc0D070aSIBmlWW3-PZT9efvcrHMi_1hk'
## TOKEN DO PeppaTest
# telegram_token = '811861359:AAED0Cm5j0c1D_hMkUbBTNJU-bIMfa3EcRo'
## TOKEN DO TeleWeather
telegram_token = '609279282:AAGSejkH6fvq4iVY2wjohK0dLl-3MN5Ry-0'

open_weather_token = '2a6a25c487d5b3c8b34d9bc0ea1909f3'


bot = WeatherBot(telegram_token, open_weather_token)
bot.run_forever()
