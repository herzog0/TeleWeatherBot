import firebase_admin

from firebase_admin import credentials
from firebase_admin import firestore
from google.cloud.exceptions import NotFound
from datetime import datetime

from .user_keys import UserDataKeys, UserStateKeys

from TOKENS_HERE import FIREBASE_CERTIFICATE


def __get_value(user_chat_id: str, key: str):
    """
    :param user_chat_id: chat_id talking to the bot
    :param key: retrieve value from this key, or key path
    :return: retrieved value or None
    """
    
    try:
        __cred = credentials.Certificate(FIREBASE_CERTIFICATE)
        firebase_admin.initialize_app(__cred)
        users = firestore.client().collection(u'users')
        response = users.document(user_chat_id).get().get(key)
        for item in UserStateKeys:
            if response == item.value:
                response = item
        return response
    except KeyError:
        print(f"Key {key} doesn't exist to the {user_chat_id} document")
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


def update(user_chat_id: str, key: UserDataKeys, value):
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

    if key is UserDataKeys.SUBSCRIBED_COORDS or key is UserDataKeys.NOTIFICATION_COORDS:
        if not (isinstance(value, dict) or ("lat" in value and "lng" in value)):
            raise TypeError("Coordinates should have a {'lat': <value>, 'lng': <value>} value structure")

    if isinstance(value, UserStateKeys):
        value = value.value

    __cred = credentials.Certificate(FIREBASE_CERTIFICATE)
    firebase_admin.initialize_app(__cred)
    users = firestore.client().collection(u'users')

    try:
        users.document(user_chat_id).update(
            {key.value: value, UserDataKeys.LAST_UPDATE.value: datetime.now().timestamp()})
    except NotFound:
        users.document(user_chat_id).set({})
        users.document(user_chat_id).update(
            {key.value: value, UserDataKeys.LAST_UPDATE.value: datetime.now().timestamp()})


def remove_key(user_chat_id: str, key: UserDataKeys):
    """
    :param user_chat_id: chat_id talking to the bot
    :param key: field to be removed
    :return: None

    This method has the ethos of making concise user information.
    Use it whenever a field is not going to be used anymore. Don't keep None values in the database fields.

    """

    try:
        __cred = credentials.Certificate(FIREBASE_CERTIFICATE)
        firebase_admin.initialize_app(__cred)
        users = firestore.client().collection(u'users')
        users.document(user_chat_id).update({
            key.value: firestore.firestore.DELETE_FIELD
        })
    except NotFound:
        return None
