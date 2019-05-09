"""
O parser propriamente
"""
import enchant
from .question import QuestionType, CouldNotUnderstandException
from datetime import datetime, timedelta
from calendar import monthrange
from operator import itemgetter


def address(bot, place_name):

    full_address, coordinates = bot.gmaps.get_user_address_by_name(place_name)

    return full_address, coordinates


def list_of_suggestions(words):
    d = enchant.Dict('pt_BR')
    full_suggestions = []
    for word in words:
        full_suggestions.append(d.suggest(word))
    return full_suggestions


def find_days_of_forecast(text: str):
    """A partir do dia atual, retorna
    uma lista com todos os dias que devem aparecer na previsão.
    Os objetos desta lista são do tipo datetime.datetime.
    No máximo 5 dias após o dia atual (contando com ele) são válidos para pesquisa.
    Ordem dos dias da semana de acordo com datetime.datetime.

    Retorna uma lista com dicionários.
    Cada dicionário contém o índice em que aquele dia aparece
    na frase do usuário e sua respectiva data.
    """

    week_days = ['segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado', 'domingo']

    words = text.lower().strip().split()
    sug_words = list_of_suggestions(words)

    days = {'month': {}, 'week': {}}

    i = 0
    while i < len(words):
        try:
            int(words[i])
            days['month'][i] = int(words[i])
            words[0] = ""
        except ValueError:
            i += 1
            continue
        i += 1

    print(sug_words)
    i = 0
    while i < len(sug_words):
        j = 0
        while j < len(sug_words[i]):
            if sug_words[i][j] in week_days:
                days['week'][i] = week_days.index(sug_words[i][j])
            j += 1
        sug_words[i] = ""
        i += 1

    """Aqui já temos todos os dias pedidos pelo usuário, devemos encontrar suas datas respectivas, se estas forem
    menores do que 5 dias à frente"""

    def less_than_five_days(value, m=False, w=False):

        if w:
            now = datetime.now()
            wk_days_left = 7 - now.weekday()

            if value - now.weekday() >= 5:
                raise ValueError(f"*Este dia ({week_days[value]}) está muito distante*")

            elif value - now.weekday() < 0:
                delta_days = wk_days_left + value

                if delta_days > 5:
                    raise ValueError(f"*Este dia ({week_days[value]}) está muito distante*")

            else:
                delta_days = value - now.weekday()

            if not delta_days and not delta_days == 0:
                raise ValueError(f"*Esta data (dia {value} semana) nao faz o menor sentido.*")

            return now + timedelta(delta_days)

        elif m:
            now = datetime.now()

            """# se não for maior igual a um, tá errado se for maior que o range desse mês, significa que se refere ao
             fim do mês seguinte e portanto, é maior que 5 dias."""

            if not 1 <= value <= monthrange(now.year, now.month)[1]:
                raise ValueError(f"*A data que você inseriu (dia {value}) não existe ou está muito distante.*")

            mth_days_left = monthrange(now.year, now.month)[1] - now.day

            # se a data estiver muito à frente

            if value - now.day > 5:
                raise ValueError(f"*A data inserida (dia {value}) está muito distante.*")

            # se a data estiver abaixo do dia de hoje, suponha que estamos falando do mes que vem

            elif value - now.day < 0:
                delta_days = mth_days_left + value

                if delta_days > 5:
                    raise ValueError(f"*A data inserida (dia {value} do mês que vem) está muito distante.*")

            # se estiver no intervalo de 5 dias
            else:
                delta_days = value - now.day

            if not delta_days and not delta_days == 0:
                raise ValueError(f"*Esta data (dia {value} mês) nao faz o menor sentido.*")

            return now + timedelta(delta_days)

    dates = []

    for i, v in days['month'].items():
        try:
            r = less_than_five_days(v, m=True)
            ddate = {'index': i, 'date': r}
            dates.append(ddate)
        except ValueError as e:
            raise e

    for i, v in days['week'].items():
        try:
            r = less_than_five_days(v, w=True)
            ddate = {'index': i, 'date': r}
            dates.append(ddate)
        except ValueError as e:
            raise e

    return dates


def find_request_types(text: str):
    words = text.lower().strip().split()
    sug_words = list_of_suggestions(words)

    when_dict = {QuestionType.WHEN: ['quando']}

    weather_dict = {QuestionType.WEATHER: ['clima', 'tempo', 'previsao', 'previsão', 'previa', 'provisor', 'prosa']}

    temperature_dict = {QuestionType.TEMPERATURE: ['temperatura', 'calor', 'frio', 'quente']}

    humidity_dict = {QuestionType.HUMIDITY: ['umidade', 'humidade', 'abafado', 'abafar']}

    rainy_dict = {QuestionType.IS_RAINY: ['chover', 'chuva', 'chove', 'choveu', 'choverá', 'chovera',
                                          'pingar', 'molhar']}

    sunny_dict = {QuestionType.IS_SUNNY: ['sol']}

    cloudy_dict = {QuestionType.IS_CLOUDY: ['nublado', 'nuvem', 'sombra']}

    weather_dicts = [when_dict,
                     weather_dict,
                     temperature_dict,
                     humidity_dict,
                     rainy_dict,
                     sunny_dict,
                     cloudy_dict]

    requests = []

    for sgwd in range(0, len(sug_words)):
        # Para cada lista de palavras sugeridas
        for qtdict in weather_dicts:
            # Para cada dicionário em weather_dicts

            tags = [tag for tag in qtdict.values()][0]
            # A lista de tags para cada question type

            if any(possible_tag in tags for possible_tag in sug_words[sgwd]):
                # Se qualquer palavra na lista de palavras  sugeridas for encontrada na lista de tags

                key = [k for k in qtdict.keys()][0]
                drequest = {'index': sgwd, 'tag': key}
                requests.append(drequest)
                break
    return requests


def find_tag_date_pairs(requests: list):

    pairs = []

    i = 0
    while i < len(requests) - 1:
        if 'tag' in requests[i]:
            j = i + 1
            while j < len(requests):
                if 'date' in requests[j]:
                    pairs.append((requests[i], requests[j]))
                    j += 1
                else:
                    break
        i += 1

    return pairs


"""Parser das entradas dos usuários"""


def parse(bot, chat_id, text: str) -> tuple:
    """Tentar ler a questão do usuário e decidir seu tipo e o que precisa para respondê-lo"""

    # TODO MELHORAR O ENTENDIMENTO DE PERGUNTAS SOBRE O CLIMA

    words = text.lower().strip().split()

    if words[0] in ['/set_dev_functions_on']:
        return QuestionType.DEV_FUNCTIONS_ON, None

    elif words[0] in ['/set_dev_functions_off']:
        return QuestionType.DEV_FUNCTIONS_OFF, None

    elif words[0] in ['/devhelp']:
        return QuestionType.DEV_COMMANDS, None

    elif words[0] in ['/cadastro', 'cadastro', 'cadastrar']:
        return QuestionType.SET_SUBSCRIPTION, None

    elif words[0] in ['/start', 'start', 'começar', 'comecar', 'inicio', 'início', 'oi', 'ola']:
        return QuestionType.INITIAL_MESSAGE, None

    elif words[0] in ['/help', 'help', '/ajuda', 'ajuda', 'socorro']:
        return QuestionType.HELP_REQUEST, None

    for word in words:
        if word in ('alarme', 'alerta', 'aviso', 'avise', 'notificacao', 'not'):
            return QuestionType.SET_ALARM, None

    """ Se não for nenhum dos comandos funcionais, tente encontrar a requisição climática """

    if ('em' not in words and not bot.users_dict[chat_id][UserKeys.SUBSCRIBED_PLACE]) or words.index('em') == len(words)-1:
        raise CouldNotUnderstandException("*Não sei se entendi um local de pesquisa*.\n"
                                          "Você não possui um lugar cadastrado. Neste caso, lembre-se de inserir o nome"
                                          " do lugar ao final da frase (e apenas um lugar), antecedido pela palavra "
                                          "*em*.\n *ex.*: previsao dia 14 e quarta feira em shopping dom pedro. \n"
                                          "Para mais informações, digite '*ajuda pesquisa*'")
    else:
        location = None
        place_name = ""
        if 'em' in words:
            place_name = words[words.index('em') + 1:]
            place_name = " ".join(place_name)
            location = address(bot, place_name)
            if not location:
                raise CouldNotUnderstandException("*Infelizmente não encontrei um local de pesquisa válido.* Tente "
                                                  "inserir outro nome após a palavra-chave *em*.")
            request = words[:words.index('em')]
        else:
            request = words

        request = " ".join(request)

        forecast_days = find_days_of_forecast(request)
        req_types = find_request_types(request)
        all_values = req_types + forecast_days
        sorted_requests = sorted(all_values, key=itemgetter('index'))
        for item in sorted_requests:
            print(item)

        pairs = find_tag_date_pairs(sorted_requests)

        for pair in pairs:
            print(pair)

        return sorted_requests, location


class UserKeys:
    SETTING_NOTIFICATION_LOCATION = 'SETTING_NOTIFICATION_LOCATION'
    SUBSCRIBING = 'SUBSCRIBING'
    FORECAST = 'FORECAST'
    MSG_TIME_DELTA = 'MSG_TIME_DELTA'
    NOTF_COORDS = 'NOTF_COORDS'
    SUBSCRIBED_PLACE = 'SUBSCRIBED_PLACE'
