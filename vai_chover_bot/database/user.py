from ..database.user_keys import UserDataKeys, UserStateKeys


class User(object):
    """
    Classe User, responsável por definir um usuário a ser referenciado no banco de dados.
    """

    def __init__(self, chat_id=None, name=None, email=None, place=None, last_update_time=None, notification_coords=None,
                 setting_notification_location=None, subscribing=None, forecast=None, subscribed_place=None,
                 subscribing_name=None, subscribing_email=None, subscribing_place=None):

        self.chat_id = chat_id
        self.name = name
        self.email = email
        self.place = place
        self.last_update_time = last_update_time
        self.notification_coords = notification_coords
        self.setting_notification_location = setting_notification_location
        self.subscribing = subscribing
        self.forecast = forecast
        self.subscribed_place = subscribed_place
        self.subscribing_name = subscribing_name
        self.subscribing_email = subscribing_email
        self.subscribing_place = subscribing_place

    def to_dict(self):
        dest = {
            self.chat_id: {
                u'name': self.name,
                u'email': self.email,
                u'place': self.place,
                u'last_update_time': self.last_update_time,
                u'notification_coords': self.notification_coords,
                u'setting_notification_location': self.setting_notification_location,
                u'subscribing': self.subscribing,
                u'forecast': self.forecast,
                u'subscribed_place': self.subscribed_place,
                u'subscribing_name': self.subscribing_name,
                u'subscribing_email': self.subscribing_email,
                u'subscribing_place': self.subscribing_place
            }
        }
        return dest

    def __repr__(self):
        
        user_string = f"""
name: {self.name}
email: {self.email}
place: {self.place}
last_update_time: {self.last_update_time}
notification_coords: {self.notification_coords}
setting_notification_location: {self.setting_notification_location}
subscribing: {self.subscribing}
forecast: {self.forecast}
subscribed_place: {self.subscribed_place}
subscribing_name: {self.subscribing_name}
subscribing_email: {self.subscribing_email}
subscribing_place: {self.subscribing_place}
"""
        
        return user_string
