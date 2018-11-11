import datetime
import json
import re
import requests
import string

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from colorama import Fore, init

from ClivoBot.settings import DIALOG_ACCESS_TOKEN
from main.models import History, DataUser, DailyEmotions

init()


class CallBackAPIView(APIView):
    INTENTS = [
        {
            'intent': 'i_welcome_ask_jobcoach_name',
            'param': ['user_name'],
            'validate': False,
            'chat': 0
        },
        {
            'intent': 'i_welcome_ask_user_email',
            'param': ['jobcoach_name'],
            'validate': False,
            'chat': 0
        },
        {
            'intent': 'i_welcome_ask_gender',
            'param': ['email'],
            'validate': False,
            'chat': 0
        },
        {
            'intent': 'i_welcome_ask_emotions',
            'param': ['user_gender'],
            'validate': True,
            'chat': 0
        },
        {
            'intent': 'i_welcome_jobcoach_contact_onboard',
            'param': ['emotion_neg'],
            'validate': True,
            'chat': 0
        },
        # Hola
        {
            'intent': 'i_starting_day_ask_emotions',
            'validate': False,
            'chat': 0
        },
        {
            'intent': 'i_starting_day_ask_workspace',
            'param': ['emotion_neg', 'emotions_pos'],
            'validate': True,
            'chat': 1
        },
        {
            'intent': 'i_jobcoach_contact',
            'param': ['emotion_neg'],
            'validate': True,
            'chat': 1
        },
        {
            'intent': 'i_first_ask_obstacles',
            'param': ['emotions_pos', 'emotion_neg'],
            'validate': True,
            'chat': 2
        },
        {
            'intent': 'i_first_describes_problem_bothers',
            'param': ['first_problem'],
            'validate': False,
            'chat': 2
        },
        {
            'intent': 'i_first_checking_ask_alerts_total',
            'validate': False,
            'chat': 2
        },
        {
            'intent': 'i_first_ask_alerts_critical',
            'param': ['alerts_total'],
            'validate': False,
            'chat': 2
        },
        {
            'intent': 'i_first_ask_alerts_non-critical',
            'param': ['alerts_critical'],
            'validate': False,
            'chat': 2
        },
    ]

    def post(self, request, format=None):
        session = self.request.data['session']
        self.save_json(self.request.data, session)
        # print(json.dumps(self.request.data))
        if "queryResult" in self.request.data:
            if "intent" in self.request.data["queryResult"]:
                intent = self.request.data["queryResult"]["intent"]["displayName"]
                print(Fore.BLUE, intent)
                data_filter = list(filter(lambda dict_intent: dict_intent['intent'] == intent, self.INTENTS))
                if len(data_filter) > 0:
                    obj_dict = data_filter[0]
                    if 'param' in obj_dict:
                        for p in obj_dict['param']:
                            if p in self.request.data["queryResult"]["parameters"]:
                                param = p
                        validate = obj_dict['validate']
                        chat = obj_dict['chat']
                        if chat > 0:
                            value = self.request.data["queryResult"]["parameters"][param]
                            print(Fore.RED, value)
                            if validate:
                                self.validate_data_daily_emotion(param, value, chat)
                            else:
                                self.create_emotion(param, value, chat)
                        else:
                            if "parameters" in self.request.data["queryResult"]:
                                value = self.request.data["queryResult"]["parameters"][param]
                                print(Fore, "ando aca")
                                if validate:
                                    self.validate_data(param, value)
                                else:
                                    self.update_data_user(param, value)

        response = {
            "fulfillmentMessages": self.generate_response(data=self.request.data["queryResult"]["fulfillmentMessages"])}
        return Response(data=response, status=status.HTTP_200_OK, content_type="application/json; charset=UTF-8")

    def create_emotion(self, param, value, chat):
        obj, created = DailyEmotions.objects.get_or_create(flow=chat, session_id=self.request.data['session'],
                                                           created__date=datetime.date.today())
        DailyEmotions.objects.filter(pk=obj.id).update(**{param: value})

    def get_or_create_data(self):
        obj, created = DataUser.objects.get_or_create(session_id=self.request.data['session'])
        return obj

    def update_data_user(self, parameter, value):
        obj = self.get_or_create_data()
        DataUser.objects.filter(pk=obj.id).update(**{parameter: value})

    def validate_data(self, param, value):
        if param == "user_gender":
            if value.lower() == "masculino":
                self.update_data_user(param, 1)
            elif value.lower() == "femenino":
                self.update_data_user(param, 2)
        elif param == "emotion_neg":
            value = ''.join([i for i in value.lower() if i in string.ascii_lowercase]).strip()
            if value == "triste":
                self.update_data_user(param, 2)
            elif value == "frustrado":
                self.update_data_user(param, 1)
            elif value == "irritado":
                self.update_data_user(param, 3)

    def validate_data_daily_emotion(self, param, value, chat):
        print(Fore.GREEN, param)
        print(Fore.GREEN, value)
        if param == "emotion_neg":
            value = ''.join([i for i in value.lower() if i in string.ascii_lowercase]).strip()
            if value == "triste":
                self.create_emotion(param, 4, chat)
            elif value == "frustrado":
                self.create_emotion(param, 3, chat)
            elif value == "irritado":
                self.create_emotion(param, 5, chat)
        elif param == "emotions_pos":
            value = ''.join([i for i in value.lower() if i in string.ascii_lowercase]).strip()
            if value == "feliz":
                self.create_emotion(param, 1, chat)
            elif value == "emocionado":
                self.create_emotion(param, 2, chat)

    def save_json(self, json_data, session):
        History.objects.create(
            data=json_data, session=session
        )

    def fetch_value(self, param):
        obj = self.get_or_create_data()
        return getattr(obj, param)

    def generate_response(self, data):
        for messages in data:
            lista = []
            if 'text' in messages:
                if 'text' in messages['text']:
                    for x in messages['text']['text']:
                        lista.append(self.validate_string(x))
                    messages['text']['text'] = lista
        return data

    def validate_string(self, phrase):
        phrase_split = re.split(' |, |! |\n', phrase)
        words = [word for word in phrase_split if re.match("\$\w+$", word)]
        if len(words) > 0:
            for word in words:
                field = word[1:]
                new_word = self.fetch_value(field)
                phrase = phrase.replace(word, new_word)
            return phrase
        else:
            return phrase


class Event:

    @classmethod
    def event(cls):
        r = requests.post(
            url="https://api.dialogflow.com/v1/",
            headers={
                "Authorization": "Bearer {}".format(DIALOG_ACCESS_TOKEN),
                "Content-Type": "application/json"
            },
            data={
                "v": "20150910",
                "lang": "es",
                "sessionId": "12345",
                "timezone": "America/Chicago"
            }
        )
        print(r)
        print(r.status_code)
        print(r.text)
