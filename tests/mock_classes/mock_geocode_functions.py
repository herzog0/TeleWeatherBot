
class GeoMock(object):

    @staticmethod
    def get_user_address_by_coordinates(lat: float, lon: float):
        if not lat and not lon:
            raise LocationNotFoundException("Nenhuma coordenada")
        return lat, lon

    @staticmethod
    def get_user_address_by_name(loc_name):
        if isinstance(loc_name, dict):
            loc_name = f'{loc_name["lat"]} {loc_name["lng"]}'
        loc = loc_name

        if not loc:
            raise LocationNotFoundException("Nenhum nome")
        return loc, None


class LocationNotFoundException(Exception):
    def __init__(self, source_text: str = None):
        if source_text:
            self.source_text = source_text
