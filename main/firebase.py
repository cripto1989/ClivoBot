import firebase_admin 
from firebase_admin import credentials
from firebase_admin import db
from django.conf import settings

cred = credentials.Certificate('credentials.json')
firebase_admin.initialize_app(cred, {
   'databaseURL': settings.FIREBASE_APP_CLIVO
})

class CustomFirebase:

   @classmethod
   def get_users(cls):
      ref = db.reference('Users')
      data = ref.get()
      return data



