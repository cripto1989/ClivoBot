import firebase_admin 
from firebase_admin import credentials
from firebase_admin import db
from django.conf import settings

cred = credentials.Certificate('{}/credentials.json'.format(settings.ROOT_DIR))
firebase_admin.initialize_app(cred, {
   'databaseURL': settings.FIREBASE_APP_CLIVO,
})

class CustomFirebase:
   """
   This class let us get information from FireBase
   """

   @classmethod
   def get_users(cls):
      """
      Get all the users saved in Firebase.
      :return dict Data of all users saved in Firebase
      """
      ref = db.reference('Users')
      data = ref.get()
      return data

   @classmethod
   def get_coach_email(cls, member_email):
      """      
      Get the email coach in firebase data.
      :param emails: List of emails related a member e.g ['email@domain.com','another@domain.com']
      """
      emails = [] 
      data = cls.get_users()
      for value in data.values():       
         if 'members' in value: 
            for member in value['members'].values(): 
               if member['email'] == member_email: 
                  emails.append(value['email'])
      print(emails)
      return emails
      



