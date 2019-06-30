import firebase_admin
from firebase_admin import firestore
from google.cloud.exceptions import NotFound
from datetime import datetime

from .user_keys import UserDataKeys, UserStateKeys

try:
    firebase_admin.initialize_app()
except ValueError:
    pass

__users = None


def __get_value(user_chat_id: str, key: str):
    """
    :param user_chat_id: chat_id talking to the bot
    :param key: retrieve value from this key, or key path
    :return: retrieved value or None
    """
    try:
        global __users
        if not __users:
            __users = firestore.client().collection(u'users')
        response = __users.document(user_chat_id).get().get(key)
        for item in UserStateKeys:
            if response == item.value:
                response = item
        return response
    except KeyError:
        return None


def name(user_chat_id: str):
    """
    :param user_chat_id: chat_id talking to the bot
    :return: user name or None
    """
    return __get_value(user_chat_id, UserDataKeys.NAME.value)


def email(user_chat_id: str):
    """
    :param user_chat_id: chat_id talking to the bot
    :return: user email or None
    """
    return __get_value(user_chat_id, UserDataKeys.EMAIL.value)


def subscribed_coords(user_chat_id: str):
    """
    :param user_chat_id: chat_id talking to the bot
    :return: coordinates for subscribed place or None
    """
    return __get_value(user_chat_id, UserDataKeys.SUBSCRIBED_COORDS.value)


def notification_coords(user_chat_id: str):
    """
    :param user_chat_id: chat_id talking to the bot
    :return: coordinates set for notification or None
    """
    return __get_value(user_chat_id, UserDataKeys.NOTIFICATION_COORDS.value)


def last_update(user_chat_id: str):
    """
    :param user_chat_id: chat_id talking to the bot
    :return: user's last update time of the form firestore.SERVER_TIMESTAMP
    """
    return __get_value(user_chat_id, UserDataKeys.LAST_UPDATE.value)


def state(user_chat_id: str):
    """
    :param user_chat_id: chat_id talking to the bot
    :return: user state or None
    """
    return __get_value(user_chat_id, UserDataKeys.STATE.value)


def has_trigger(user_chat_id: str):
    """
    :param user_chat_id: chat_id talking to the bot
    :return: return true if user has subscribed a trigger
    """
    alert = __get_value(user_chat_id, UserDataKeys.ALERT.value)
    return True if alert.get("TRIGGER", None) else False


def has_daily_alert(user_chat_id: str):
    """
    :param user_chat_id: chat_id talking to the bot
    :return: return true if user has subscribed a daily alert
    """
    alert = __get_value(user_chat_id, UserDataKeys.ALERT.value)
    return True if alert.get("TRIGGER", None) else False


def update(user_chat_id: str, args_dict):
    # key: UserDataKeys, value
    """
    :param user_chat_id: chat_id talking to the bot

    :param key: user information key to be created/updated,
    keys are enum objects from :attr:`~.user_keys`

    :param value: value to be written in the user key field

    :return: None


    This method is responsible for creating or updating an existing
    user document in the firebase cloud.
    There is no "write" method available, only this one.

    If the document doesn't exist, it is created and then updated with
    the passed arguments.

    This makes a cleaner and less error susceptible code.

    """
    update_dict = {}
    for key, value in args_dict.items():
        if key is UserDataKeys.SUBSCRIBED_COORDS or key is UserDataKeys.NOTIFICATION_COORDS:
            if not (isinstance(value, dict) or ("lat" in value and "lng" in value)):
                raise TypeError("Coordinates should have a {'lat': <value>, 'lng': <value>} value structure")
        if isinstance(value, UserStateKeys):
            value = value.value

        update_dict.update({key, value})

    update_dict.update({UserDataKeys.LAST_UPDATE.value: datetime.now().timestamp()})

    global __users
    if not __users:
        __users = firestore.client().collection(u'users')

    try:
        __users.document(user_chat_id).update(update_dict)
    except NotFound:
        __users.document(user_chat_id).set({})
        __users.document(user_chat_id).update(update_dict)


def remove_key(user_chat_id: str, key: UserDataKeys):
    """
    :param user_chat_id: chat_id talking to the bot
    :param key: field to be removed
    :return: None

    This method has the ethos of making concise user information.
    Use it whenever a field is not going to be used anymore. Don't keep None values in the database fields.

    """

    try:
        global __users
        if not __users:
            __users = firestore.client().collection(u'users')
        __users.document(user_chat_id).update({
            key.value: firestore.firestore.DELETE_FIELD
        })
        return True
    except NotFound:
        return None
