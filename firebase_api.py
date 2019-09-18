import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
import config


cred = credentials.Certificate(config.FIREBASE_CRED)
default_app = firebase_admin.initialize_app(cred)

db = firestore.client()


def upload_highscore(score, name, time):
    doc_ref = db.collection(u'highscores').document()
    doc_ref.set({
        'date': time,
        'score': score,
        'name': name,
        'clientID': config.CABINET_ID,
        'location': config.LOCATION,
        'freemode': config.FREE_MODE
    })


def print_all_scores():
    docs = db.collection(u'highscores').order_by('score', direction=firestore.Query.DESCENDING).stream()
    for doc in docs:
        print(u'{} => {}'.format(doc.id, doc.to_dict()))


