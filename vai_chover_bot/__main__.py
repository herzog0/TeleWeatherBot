
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
        google_maps_token = variables['GOOGLEMAPSTOKEN']
        password = ""
        try:
            password = variables['PASSWORD']
        except KeyError:
            print("No password set, dev options not avaiable")

        bot = WeatherBot(telegram_token, open_weather_token, google_maps_token, password)
        bot.run_forever()

    except KeyError as key:
        print(f'Erro ao encontrar o token {key}.\nTenha certeza de que os tokens estão de acordo com o modelo citado no'
              ' arquivo README.md\n')
    except FileNotFoundError:
        print('O arquivo "TOKENS_HERE" deve ser criado na pasta raiz do projeto!\n')

