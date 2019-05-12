from tele_weather_bot.bot import WeatherBot
import TOKENS_HERE


def main():
    try:
        password = ''
        try:
            if not TOKENS_HERE.PASSWORD:
                raise NameError
            password = TOKENS_HERE.PASSWORD
        except NameError:
            print("No password set, dev options not avaiable")

        bot = WeatherBot(telegram_token=TOKENS_HERE.TELEGRAM_TOKEN,
                         open_weather_token=TOKENS_HERE.OWM_TOKEN,
                         google_maps_token=TOKENS_HERE.GOOGLEMAPS_TOKEN,
                         firebase_certificate=TOKENS_HERE.FIREBASE_CERTIFICATE,
                         password=password)
        bot.run_forever()

    except NameError as e:
        print(str(e))
