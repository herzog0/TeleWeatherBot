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
                         password=password)
        bot.run_forever()

    except NameError as e:
        print(str(e))
    except AttributeError as e:
        print(str(e))
    except ImportError as e:
        print(str(e))
