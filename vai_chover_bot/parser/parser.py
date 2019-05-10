"""
O parser propriamente
"""
import enchant
from .question import WeatherTypes, FunctionalTypes, CouldNotUnderstandException
import datetime
from datetime import timedelta
from datetime import date as date_type
from calendar import monthrange


def address(bot, place_name):

    full_address, coordinates = bot.gmaps.get_user_address_by_name(place_name)

    return full_address, coordinates


def list_of_suggestions(word: str):
    if not len(word.split()) == 1:
        raise ValueError("lista de sugestões deve receber apenas uma palavra")
    d = enchant.Dict('pt_BR')
    return d.suggest(word)


def find_date(word: str):
    """
    Retorna a data correspondente à palavra inserida
    """

    week_days = ['segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado', 'domingo',
                 'amanha',
                 'haja', 'hoje', 'agora']

    # 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10

    def less_than_five_days(value, m=False, w=False):

        if w:
            now = datetime.datetime.now()
            wk_days_left = 7 - now.weekday()

            if 0 <= value - now.weekday() <= 5:
                delta_days = value - now.weekday()
            elif 0 <= wk_days_left + value <= 5:
                delta_days = wk_days_left + value
            else:
                raise MoreThanFiveDaysException(f"*{week_days[value].capitalize()} está muito distante*\n"
                                                f"Escolha uma data no máximo 5 dias à frente")

            if not delta_days and not delta_days == 0:
                raise MoreThanFiveDaysException(f"*{value} nao faz o menor sentido.*")

            return now + timedelta(delta_days)

        elif m:
            now = datetime.datetime.now()

            # se não for maior igual a um, tá errado se for maior que o range desse mês, significa que se refere ao
            # fim do mês seguinte e portanto, é maior que 5 dias.

            if not 1 <= value <= monthrange(now.year, now.month)[1]:
                raise MoreThanFiveDaysException(
                    f"*O dia {value} não existe ou está muito distante*\n"
                    f"Escolha uma data no máximo 5 dias à frente")

            mth_days_left = monthrange(now.year, now.month)[1] - now.day

            # se a data estiver muito à frente

            if 0 <= value - now.day <= 5:
                delta_days = value - now.day
            elif 0 <= mth_days_left + value <= 5:
                delta_days = mth_days_left + value
            else:
                raise MoreThanFiveDaysException(f"*Dia {value}) está muito distante*\n"
                                                f"Escolha uma data no máximo 5 dias à frente")

            if not delta_days and not delta_days == 0:
                raise MoreThanFiveDaysException(f"*Dia {value} mês) nao faz o menor sentido")

            return now + timedelta(delta_days)

    word = word.lower().strip()
    try:
        int(word)
        return less_than_five_days(int(word), m=True)
    except ValueError:
        sug_words = list_of_suggestions(word)
        try:
            day_index = week_days.index(list(filter(lambda x: x in week_days, sug_words))[0])
        except IndexError:
            return []
        if day_index in [8, 9, 10]:
            return less_than_five_days(datetime.datetime.now().weekday(), w=True)
        elif day_index == 7:
            return less_than_five_days((datetime.datetime.now().weekday() + 1) % 7, w=True)
        else:
            return less_than_five_days(day_index, w=True)
    except MoreThanFiveDaysException as e:
        raise e


def find_request_type(word: str):
    sug_words = list_of_suggestions(word)

    for weather_type in WeatherTypes:
        if any(word in weather_type.value for word in sug_words):
            return weather_type


def find_hour(word: str):
    words = word.split('h')
    if len(words) == 1:
        return
    try:
        if not 0 <= int(words[0]) <= 23:
            return
        return words[0]
    except ValueError:
        return


def find_tag_date_pairs(requests: list):

    pairs = []

    i = 0
    while i < len(requests) - 1:
        if isinstance(requests[i], WeatherTypes):
            j = i + 1
            while j < len(requests):
                if isinstance(requests[j], date_type):

                    date_index = j

                    _date = requests[j]
                    j += 1
                    while j < len(requests) and requests[j] == []:
                        j += 1

                    if isinstance(requests[j], int):
                        _date = requests[date_index].replace(hour=requests[j])

                    pairs.append((requests[i], _date))
                else:
                    break
        i += 1

    if isinstance(requests[len(requests) - 1], WeatherTypes):
        pairs.append((requests[i], datetime.datetime.now()))

    return pairs


"""Parser das entradas dos usuários"""


def parse(bot, chat_id, text: str) -> tuple:
    """Tentar ler a questão do usuário e decidir seu tipo e o que precisa para respondê-lo"""

    words = text.lower().strip().split()

    for functional_type in FunctionalTypes:
        if any(word in functional_type.value for word in words):
            return functional_type, None

    # Se não for nenhum dos comandos funcionais, tente encontrar a requisição climática

    if ('em' not in words and not bot.users_dict[chat_id][UserKeys.SUBSCRIBED_PLACE]) or \
            words.index('em') == len(words) - 1:
        raise CouldNotUnderstandException("*Não sei se entendi um local de pesquisa*.\n"
                                          "Você não possui um lugar cadastrado. Neste caso, lembre-se de inserir o nome"
                                          " do lugar ao final da frase (e apenas um lugar), antecedido pela palavra "
                                          "*em*.\n *ex.*: previsao dia 14 e quarta feira em shopping dom pedro. \n"
                                          "Para mais informações, digite '*ajuda pesquisa*'")
    else:
        location = None
        if 'em' in words:
            place_name = words[words.index('em') + 1:]
            place_name = " ".join(place_name)
            location = address(bot, place_name)
            if not location:
                raise CouldNotUnderstandException("*Infelizmente não encontrei um local de pesquisa válido.* Tente "
                                                  "inserir outro nome após a palavra-chave *em*.")
            sentence = words[:words.index('em')]
        else:

            # todo location = bot.get_user_data(chat_id, location=True)
            sentence = words

        request = []
        for word in sentence:
            try1 = find_date(word)
            try2 = find_request_type(word)
            try3 = find_hour(word)
            if try1:
                request.append(try1)
            elif try2:
                request.append(try2)
            elif try3:
                request.append(int(try3))
            else:
                request.append([])

        pairs = find_tag_date_pairs(request)

        return pairs, location


class MoreThanFiveDaysException(Exception):
    def __init__(self, source_text: str = None):
        if source_text:
            self.source_text = source_text


class UserKeys:
    SETTING_NOTIFICATION_LOCATION = 'SETTING_NOTIFICATION_LOCATION'
    SUBSCRIBING = 'SUBSCRIBING'
    FORECAST = 'FORECAST'
    MSG_TIME_DELTA = 'MSG_TIME_DELTA'
    NOTF_COORDS = 'NOTF_COORDS'
    SUBSCRIBED_PLACE = 'SUBSCRIBED_PLACE'
