import firebase_admin
import os
from firebase_admin import credentials
from firebase_admin import firestore

from .user import User


class UserDAO(object):
    def __init__(self, firebase_certificate):
        cred = credentials.Certificate(firebase_certificate)
        firebase_admin.initialize_app(cred)

    def write(self, user):
        db = firestore.client()
        doc_ref = db.collection(u'users').document(user.chat_id).set(user.to_dict())
        return doc_ref

    def read(self, id):
        db = firestore.client()
        doc_ref = db.collection(u'users').document(id)
        return doc_ref.get().to_dict()
    
    def update(self, user):
        db = firestore.client()
        doc_ref = db.collection(u'users').document(user.id)
        doc_ref.update(user.to_dict())

    def delete(self, id):
        db = firestore.client()
        db.collection(u'users').document(id).delete()

