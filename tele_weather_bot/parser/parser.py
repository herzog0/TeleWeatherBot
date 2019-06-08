"""
O parser propriamente
"""
import datetime

from datetime import timedelta
from calendar import monthrange

from .question_keys import WeatherTypes, FunctionalTypes
from ..database.userDAO import state, subscribed_coords
from ..google_maps.geocode_functions import set_gmaps_obj, get_user_address_by_name

# adicionar variações das escritas dos dias aqui
week_days = [{0: ['segunda', 'seg', 'segnda', 'sgnda']},
             {1: ['terça', 'ter', 'terca']},
             {2: ['quarta', 'qua', 'quart', 'quata']},
             {3: ['quinta', 'qui', 'quinta']},
             {4: ['sexta', 'sext', 'sxt', 'sex']},
             {5: ['sábado', 'sabado', 'sbdo', 'sabdo', 'sab', 'sbd']},
             {6: ['domingo', 'dmg', 'dom', 'doming', 'dmingo', 'dming']},
             {(datetime.datetime.now().weekday() + 1) % 7: ['amanha', 'amanhã', 'amnh', 'amnha', 'amnhã']},
             {datetime.datetime.now().weekday(): ['haja', 'hoje', 'agora', 'hj', 'hoj', 'oge', 'oje']}]


def address(place_name):
    set_gmaps_obj()
    full_address, coordinates = get_user_address_by_name(place_name)
    return full_address, coordinates


def less_than_five_days(value, m=False, w=False):
    now = datetime.datetime.now()
    days_left = 0
    today = 0

    if w:
        today = now.weekday()
        days_left = 7 - now.weekday()

    elif m:
        today = now.day
        days_left = monthrange(now.year, now.month)[1] - now.day

        # se não for maior igual a um, tá errado se for maior que o range desse mês, significa que se refere ao
        # fim do mês seguinte e portanto, é maior que 5 dias.

        if not 1 <= value <= monthrange(now.year, now.month)[1]:
            raise MoreThanFiveDaysException(
                f"*O dia {value} não existe ou está muito distante*\n"
                f"Escolha uma data no máximo 5 dias à frente")

    if 0 <= value - today <= 5:
        delta_days = value - today
    elif 0 <= days_left + value <= 5:
        delta_days = days_left + value
    else:
        raise MoreThanFiveDaysException(f"*{week_days[value].get(value)[0].capitalize() if w else f'Dia {value}'} "
                                        f"está muito* *distante*\n"
                                        f"Escolha uma data no máximo 5 dias à frente")

    if not delta_days and not delta_days == 0:
        raise MoreThanFiveDaysException(f"*{value} nao faz o menor sentido.*")

    return now + timedelta(delta_days)


def find_date(word: str):
    """
    Retorna a data correspondente à palavra inserida
    """

    word = word.lower().strip()
    try:
        int(word)
        return less_than_five_days(int(word), m=True)
    except ValueError:
        for wd in week_days:
            if word in list(wd.values())[0]:
                return less_than_five_days(list(wd.keys())[0], w=True)

        return []
    except MoreThanFiveDaysException as e:
        raise e


def find_request_type(word: str):
    for weather_type in WeatherTypes:
        if word in weather_type.value:
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
    assert requests

    pairs = []
    last_was_tag = False
    tag = None

    for request in requests:
        if isinstance(request, WeatherTypes):
            tag = request
            last_was_tag = True

        elif isinstance(request, datetime.datetime) and tag:
            date = request
            pairs.append([tag, date])
            last_was_tag = False

        elif isinstance(request, int) and not last_was_tag:
            pairs[-1][1] = pairs[-1][1].replace(hour=request)

    if isinstance(requests[-1], WeatherTypes):
        pairs.append((requests[-1], datetime.datetime.now()))

    return pairs


def parse(chat_id: str, text: str) -> tuple:
    """Tentar ler a questão do usuário e decidir seu tipo e o que precisa para respondê-lo"""

    words = text.lower().strip().split()

    # Se inseriu comando funcional
    for functional_type in FunctionalTypes:
        if any(word in functional_type.value for word in words):
            return functional_type, None

    # Se está no meio de algum processo de inscrição
    usr_stt = state(chat_id)
    if usr_stt:
        return usr_stt, None

    # Se não for nenhum dos comandos funcionais, tente encontrar a requisição climática
    if ('em' not in words and not subscribed_coords(chat_id)) or ('em' in words and words.index('em') == words[-1]):
        raise CouldNotUnderstandException("*Não sei se entendi um local de pesquisa*.\n"
                                          "Você não possui um lugar cadastrado. Neste caso, lembre-se de inserir o nome"
                                          " do lugar ao final da frase (e apenas um lugar), antecedido pela palavra "
                                          "*em*.\n *ex.*: previsao dia 14 e quarta feira em shopping dom pedro. \n"
                                          "Para mais informações, digite '*ajuda pesquisa*'")
    else:
        if 'em' in words:
            place_name = words[words.index('em') + 1:]
            place_name = " ".join(place_name)
            location = address(place_name)
            if not location:
                raise CouldNotUnderstandException("*Infelizmente não encontrei um local de pesquisa válido.* Tente "
                                                  "inserir outro nome após a palavra-chave *em*.")
            sentence = words[:words.index('em')]
        else:
            coords = subscribed_coords(chat_id)
            coords_f = f'{coords["lat"]} {coords["lng"]}'
            location = address(coords_f)
            sentence = words

        request = []
        for word in sentence:
            try1 = find_request_type(word)
            try2 = find_date(word)
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


class CouldNotUnderstandException(Exception):
    """Exceção de não compreender a questão ou o tipo dela"""
    def __init__(self, source_text: str = None):
        """Pode conter o texto que não foi compreendido"""
        if source_text:
            self.source_text = source_text
