import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

class UserDAO(object):
    def __init__(self, db):
        self.db = db
    
    def writeNewUser(self, user):
        doc_ref = self.db.collection(u'users').document().set(user.to_dict())
        return doc_ref