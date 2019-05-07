
def main():
    try:
        variables = {}
        with open("TOKENS_HERE") as tokens:
            for line in tokens:
                variable = line.split('=')
                if len(variable) > 1:
                    var1 = variable[0]
                    token = variable[1].split('\n')[0]
                    variables[var1] = token

        from vai_chover_bot.bot import WeatherBot

        telegram_token = variables['TELEGRAM_TOKEN']
        open_weather_token = variables['OWM_TOKEN']

        bot = WeatherBot(telegram_token, open_weather_token)
        bot.run_forever()

    except KeyError as key:
        print('Variável não encontrada:', key, file=sys.stderr)

