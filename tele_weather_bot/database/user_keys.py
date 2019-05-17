from enum import Enum, unique


@unique
class UserStateKeys(Enum):

    SUBSCRIBING_DAILY_ALERT_PLACE = "SUBSCRIBING_DAILY_ALERT_PLACE"

    SUBSCRIBING_TRIGGER_ALERT_PLACE = "SUBSCRIBING_TRIGGER_ALERT_PLACE"

    SUBSCRIBING_NAME = "SUBSCRIBING_NAME"

    SUBSCRIBING_EMAIL = "SUBSCRIBING_EMAIL"

    SUBSCRIBING_PLACE = "SUBSCRIBING_PLACE"

    ALREDY_SUBSCRIBED = "ALREDY_SUBSCRIBED"


@unique
class UserDataKeys(Enum):

    CHAT_ID = "chat_id"

    NAME = "name"

    EMAIL = "email"

    SUBSCRIBED_COORDS = "subscribed_coords"

    NOTIFICATION_COORDS = "notfication_coords"
    
    STATE = "state"

    LAST_UPDATE = "last_update"
