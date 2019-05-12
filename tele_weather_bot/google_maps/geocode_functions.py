import googlemaps


class GoogleGeoCode:

    def __init__(self, google_api_token: str):
        self.gmaps = googlemaps.Client(key=google_api_token)

    def get_user_address_by_coordinates(self, lat: float, lon: float):
        loc = self.gmaps.reverse_geocode((lat, lon))
        if not loc:
            raise LocationNotFoundException("Essas coordenadas não correspondem a um lugar válido para pesquisa.")
        return loc[0]['formatted_address']

    def get_user_address_by_name(self, loc_name: str):
        loc = self.gmaps.geocode(loc_name)
        if not loc:
            raise LocationNotFoundException("Não consegui encontrar nenhum endereço correspondente.")
        return loc[0]['formatted_address'],  loc[0]['geometry']['location']


class LocationNotFoundException(Exception):
    def __init__(self, source_text: str = None):
        if source_text:
            self.source_text = source_text
