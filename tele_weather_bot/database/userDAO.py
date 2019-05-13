import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


class UserDAO(object):
    def __init__(self, firebase_certificate):
        cred = credentials.Certificate(firebase_certificate)
        firebase_admin.initialize_app(cred)

    @staticmethod
    def write(user):
        db = firestore.client()
        chat_id = str(user.user_id())
        doc_ref = db.collection(u'users').document(chat_id).set(user.to_dict())
        return doc_ref

    @staticmethod
    def read(chat_id):
        db = firestore.client()
        chat_id = str(chat_id)
        doc_ref = db.collection(u'users').document(chat_id)
        return doc_ref.get().to_dict()

    @staticmethod
    def update(user):
        db = firestore.client()
        chat_id = str(user.chat_id)
        doc_ref = db.collection(u'users').document(chat_id)
        doc_ref.update(user.to_dict())

    @staticmethod
    def delete(chat_id):
        db = firestore.client()
        chat_id = str(chat_id)
        db.collection(u'users').document(chat_id).delete()
