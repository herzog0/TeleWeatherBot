from datetime import datetime

from ..database.user_keys import UserStateKeys


class User(object):
    """
    Classe User, responsável por definir um usuário a ser referenciado no banco de dados.
    """

    def __init__(self,
                 chat_id,
                 name=None,
                 email=None,
                 place=None,
                 last_update_time=None,
                 notification_coords=None,
                 subscribing_alert=None,
                 subscribing_name=None,
                 subscribing_email=None,
                 subscribing_place=None,
                 subscribed=None):

        self.chat_id = str(chat_id)
        self.name = name
        self.email = email
        self.place = place
        self.last_update_time = last_update_time
        self.notification_coords = notification_coords
        self.subscribed = subscribed
        self.subscribing_alert = subscribing_alert
        self.subscribing_name = subscribing_name
        self.subscribing_email = subscribing_email
        self.subscribing_place = subscribing_place

    def to_dict(self):
        user_state = self.state()

        dest = {
            self.chat_id: {
                u'name': self.name,
                u'email': self.email,
                u'place': self.place,
                u'last_update_time': self.last_update_time,
                u'notification_coords': self.notification_coords,
                u'state': user_state,
            }
        }
        return dest

    def state(self):
        state = None
        if self.subscribing_name:
            state = UserStateKeys.SUBSCRIBING_NAME
        elif self.subscribing_email:
            state = UserStateKeys.SUBSCRIBING_EMAIL
        elif self.subscribing_place:
            state = UserStateKeys.SUBSCRIBING_PLACE
        elif self.subscribing_alert:
            state = UserStateKeys.SUBSCRIBING_ALERT
        return state

    def update_user(self,
                    name=None,
                    email=None,
                    place=None,
                    notification_coords=None,

                    subscribed=False,
                    subscribing_alert=False,
                    subscribing_name=False,
                    subscribing_email=False,
                    subscribing_place=False
                    ):
        # somente um estado por vez
        states = [subscribing_alert, subscribing_name, subscribing_email, subscribing_place, subscribed]
        assert len([x for x in states if x]) <= 1

        if name is not None:
            self.name = name

        if email is not None:
            self.email = email

        if place is not None:
            self.place = place

        if notification_coords:
            self.notification_coords = notification_coords

        if any([subscribing_alert, subscribing_name, subscribing_email, subscribing_place, subscribed]):
            self.subscribing_alert = subscribing_alert
            self.subscribing_name = subscribing_name
            self.subscribing_email = subscribing_email
            self.subscribing_place = subscribing_place
            self.subscribed = subscribed

        self.last_update_time = datetime.now()

    def __repr__(self):
        
        user_string = f"""
name: {self.name}
email: {self.email}
place: {self.place}
last_update_time: {self.last_update_time}
notification_coords: {self.notification_coords}
state: {self.state()}
"""
        
        return user_string
