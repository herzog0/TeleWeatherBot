import googlemaps


class GoogleGeoCode:

    def __init__(self, google_api_token: str):
        self.gmaps = googlemaps.Client(key=google_api_token)

    def get_user_address_by_coordinates(self, lat: float, lon: float):
        return self.gmaps.reverse_geocode((lat, lon))[0]['formatted_address']

    def get_user_address_by_name(self, loc_name: str):
        loc = self.gmaps.geocode(loc_name)
        assert not loc == []
        return loc[0]['formatted_address'],  loc[0]['geometry']['location']
