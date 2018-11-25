import firebase_admin 
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate('clivoapp-firebase-adminsdk-spp16-b47d63d943.json')
firebase_admin.initialize_app(cred, {
   'databaseURL': 'https://clivoapp.firebaseio.com/'
})

# As an admin, the app has access to read and write all data, regradless of Security Rules
ref = db.reference('Users')
print(ref.get())
#print(ref)

