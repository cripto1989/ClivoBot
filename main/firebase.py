import firebase_admin 
from firebase_admin import credentials
from firebase_admin import db
from django.conf.settings import FIREBASE_APP_CLIVO

cred = credentials.Certificate('credentials.json')
firebase_admin.initialize_app(cred, {
   'databaseURL': FIREBASE_APP_CLIVO
})

ref = db.reference('Users')
data = ref.get()
print(json.loads(data))

