import firebase_admin 
from firebase_admin import credentials
from firebase_admin import db
from django.conf import settings
import json

cred = credentials.Certificate('{}/credentials.json'.format(settings.ROOT_DIR))
firebase_admin.initialize_app(cred, {
   'databaseURL': settings.FIREBASE_APP_CLIVO,
})

class CustomFirebase:
   """
   This class let us get information from FireBase
   """

   @classmethod
   def get_data(cls, key_name):
      """
      Get all the users saved in Firebase.
      :paran key_name name or group of data in firebase e.g Users, Groups, etc.
      :return dict Data of all users saved in Firebase
      """
      ref = db.reference(key_name)
      data = ref.get()
      return data

   @classmethod
   def get_coach_email(cls, member_email):
      """      
      Get the email coach in firebase data.
      :param emails: List of emails related a member e.g ['email@domain.com','another@domain.com']
      """
      emails = [] 
      data = cls.get_data('Users')
      for value in data.values():       
         if 'members' in value: 
            for member in value['members'].values(): 
               if member['email'] == member_email: 
                  emails.append(value['email'])
      print(emails)
      return emails
      
   @classmethod
   def get_participants_email(cls, member_email):
      """      
      Get the email coach in firebase data.
      :param emails: List of emails related a member e.g ['email@domain.com','another@domain.com']
      """
      emails = [] 
      data = cls.get_data('Groups')
      for key,value in data.items():   
         # print(json.dumps(value))
         # print('\n')    
         if 'members' in value: 
            for member in value['members'].values(): 
               if member['email'] == member_email:
                  for participant in value['participants']:
                     # print(value['participants'][participant])
                     if value['participants'][participant]['nivel'] != 'parcial':
                        print(key)
                        emails.append(value['participants'][participant]['email'])
      print(emails)
      return emails
   


