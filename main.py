from vai_chover_bot import WeatherBot


telegram_token = '822196045:AAFc0D070aSIBmlWW3-PZT9efvcrHMi_1hk'
open_weather_token = '2a6a25c487d5b3c8b34d9bc0ea1909f3'

bot = WeatherBot(telegram_token, open_weather_token)
bot.run_forever()