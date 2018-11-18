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
            'intent': 'i_starting_day_describe_problem',
            'param': ['initial_change'],
            'validate': False,
            'chat': 1
        },
        # 1 hr
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
        {
            'intent': 'i_first_checkin_let\'s_work',
            'param': ['alerts_non-critical'],
            'validate': True,
            'chat': 2
        },
        # 2hr
        {
            'intent': 'i_second_checkin_ask_alerts_critical',
            'param': ['alerts_total'],
            'validate': False,
            'chat': 3
        },
        {
            'intent': 'i_second_checkin_ask_alerts_non-critical',
            'param': ['alerts_critical'],
            'validate': False,
            'chat': 3
        },
        {
            'intent': 'i_second_checkin_ask_emotions',
            'param': ['alerts_non-critical'],
            'validate': True,
            'chat': 3
        },
        {
            'intent': 'i_second_checkin_ask_taste_work',
            'param': ['emotions_pos'],
            'validate': True,
            'chat': 3
        },
        {
            'intent': 'i_jobcoach_contact',
            'param': ['emotion_neg', 'second_dislike'],
            'validate': True,
            'chat': 3
        },
        # 2 min
        {
            'intent': 'i_response_again',
            'validate': False,
            'chat': 0
        }
    ]

    def post(self, request, format=None):
        session = self.request.data['session']
        self.save_json(self.request.data, session)
        # Principal request
        print(json.dumps(self.request.data))
        if "queryResult" in self.request.data:
            if "intent" in self.request.data["queryResult"]:
                intent = self.request.data["queryResult"]["intent"]["displayName"]
                # Intent
                print(Fore.BLUE, intent)
                data_filter = list(filter(lambda dict_intent: dict_intent['intent'] == intent, self.INTENTS))
                if len(data_filter) > 0:
                    obj_dict = data_filter[0]
                    param = ''
                    if 'param' in obj_dict:
                        for p in obj_dict['param']:
                            if p in self.request.data["queryResult"]["parameters"]:
                                if len(self.request.data["queryResult"]["parameters"][p]) > 0:
                                    param = p
                        validate = obj_dict['validate']
                        chat = obj_dict['chat']
                        if len(param) > 0:
                            if chat > 0:
                                    value = self.request.data["queryResult"]["parameters"][param]
                                    if validate:
                                        self.validate_data_daily_emotion(param, value, chat)
                                    else:
                                        self.create_emotion(param, value, chat)
                            else:
                                if "parameters" in self.request.data["queryResult"]:
                                    value = self.request.data["queryResult"]["parameters"][param]
                                    if validate:
                                        self.validate_data(param, value)
                                    else:
                                        self.update_data_user(param, value)

        response = {
            "fulfillmentMessages": self.generate_response(data=self.request.data["queryResult"]["fulfillmentMessages"])}
        return Response(data=response, status=status.HTTP_200_OK, content_type="application/json; charset=UTF-8")

    def create_emotion(self, param, value, chat):
        if 'originalDetectIntentRequest' in self.request.data:
            slack_id = self.get_user_slack(self.request.data['originalDetectIntentRequest'])
            print(Fore.RED, slack_id)
        obj, created = DailyEmotions.objects.get_or_create(flow=chat, slack=slack_id,
                                                           created__date=datetime.date.today())
        DailyEmotions.objects.filter(pk=obj.id).update(**{param: value})

    def get_or_create_data(self, slack_id):
        try:
            obj, created = DataUser.objects.get_or_create(slack=slack_id)
            return obj
        except Exception as e:
            print('Error creando data user {}'.format(e))

    def update_data_user(self, parameter, value):
        if 'originalDetectIntentRequest' in self.request.data:
            slack_id = self.get_user_slack(self.request.data['originalDetectIntentRequest'])
        obj = self.get_or_create_data(slack_id)
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
        # print(Fore.GREEN, param)
        # print(Fore.GREEN, value)
        if param == "emotion_neg":
            # We try to get the previous name intent and validate whit this.
            type_intent_previous = self.get_output_context(self.request.data['queryResult'])
            if type_intent_previous == 'i_starting_day-followup':
                chat = 1
            elif type_intent_previous == 'i_first_checkin-followup':
                chat = 2
            value = ''.join([i for i in value.lower() if i in string.ascii_lowercase]).strip()
            print(param)
            print(value)
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
        elif param == "alerts_non-critical":
            self.create_emotion("alerts_non_critical", value, chat)
        elif param == "second_dislike":
            self.create_emotion("second_dislike", value, chat)

    def save_json(self, json_data, session):
        History.objects.create(
            data=json_data, session=session
        )

    def fetch_value(self, param):
        if 'originalDetectIntentRequest' in self.request.data:
            slack_id = self.get_user_slack(self.request.data['originalDetectIntentRequest'])
        obj = self.get_or_create_data(slack_id)
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

    def get_user_slack(self, data):
        """
        This method return slack id included in "originalDetectIntentRequest" key
        :param data: dict originalDetectIntentRequest
        :return: ID slack DE21HHWR4
        """
        user = None
        if 'payload' in data:
            if 'data' in data['payload']:
                # El slack ID puede llegar en diferentes posiciones
                if 'user' in data['payload']['data']:
                    user = data['payload']['data']['user']
                elif 'event' in data['payload']['data']:
                    if 'user' in data['payload']['data']['event']:
                        user = data['payload']['data']['event']['user']
                if isinstance(user, str):
                    return user
                elif isinstance(user, dict):
                    return user['id']


    def get_output_context(self, data):
        if 'outputContexts' in data:
            if len(data['outputContexts']) > 0:
                obj = data['outputContexts'][0]
                name = obj['name']
                name = name.split('/')[::-1][0]
                return name

    def get(self, request):
        email = self.request.query_params.get('email')
        date = self.request.query_params.get('date')
        try:
            du = DataUser.objects.get(email=email)
        except Exception as e:
            return Response(data={'text':'User doesn\'t exists'}, status=status.HTTP_400_BAD_REQUEST)
        de = DailyEmotions.objects.filter(slack=du.slack, created__date=date)
        # print(de.count())
        alert_total = 0
        alerts_critical = 0
        alerts_non_critical = 0
        work_change = ""
        first_problem = ""
        work_dislike = ""
        emotion_hola = ""
        emotion_1hr = ""
        emotion_2hr = ""
        work_taste = True
        for daily in de:
            if isinstance(daily.alerts_total, str):
                alert_total += int(daily.alerts_total)
            if isinstance(daily.alerts_critical, str):
                alerts_critical += int(daily.alerts_critical)
            if isinstance(daily.alerts_non_critical, str):
                alerts_non_critical += int(daily.alerts_non_critical)
            if isinstance(daily.initial_change, str):
                work_change = daily.initial_change
            if isinstance(daily.first_problem, str):
                first_problem = daily.first_problem
            if isinstance(daily.second_dislike, str):
                work_dislike = daily.second_dislike
        for daily in de:
            if daily.flow == DailyEmotions.FLOW.starting_day:
                if daily.emotions_pos or daily.emotion_neg:
                    emotion_hola = DailyEmotions.EMOTION[daily.emotions_pos or daily.emotion_neg]
            if daily.flow == DailyEmotions.FLOW.first_check_in:
                if daily.emotions_pos or daily.emotion_neg:
                    emotion_1hr = DailyEmotions.EMOTION[daily.emotions_pos or daily.emotion_neg]
            if daily.flow == DailyEmotions.FLOW.second_check_in:
                if daily.emotions_pos or daily.emotion_neg:
                    emotion_2hr = DailyEmotions.EMOTION[daily.emotions_pos or daily.emotion_neg]
                if daily.second_dislike:
                    work_taste = False
        data = {
            "alert_total": alert_total,
            "alerts_critical": alerts_critical,
            "alerts_non_critical": alerts_non_critical,
            "work_change": work_change,
            "first_problem": first_problem,
            "work_dislike": work_dislike,
            "emotion_hola": emotion_hola,
            "emotion_1hr": emotion_1hr,
            "emotion_2hr": emotion_2hr,
            "work_taste": work_taste
        }
        return Response(data=data, status=status.HTTP_200_OK)
