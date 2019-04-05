from . import WeatherBot
import sys
import os


try:
    telegram_token = os.environ['TELEGRAM_TOKEN']
    open_weather_token = os.environ['OWM_TOKEN']

    bot = WeatherBot(telegram_token, open_weather_token)
    bot.run_forever()

except KeyError as err:
    print('Variável não encontrada:', err, file=sys.stderr)
