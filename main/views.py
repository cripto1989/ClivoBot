import calendar
import datetime
import json
import re
import string

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from colorama import Fore, init

from main.models import History, DataUser, DailyEmotions
from main.firebase import CustomFirebase
from main.utility import SendGrid

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
                if intent == 'i_greetings':
                    slack_id = self.get_user_slack(self.request.data['originalDetectIntentRequest'])
                    du = DataUser.objects.filter(slack=slack_id)
                    if du.count() > 0:
                        du = du.last()
                        list_emails = list(set(
                            CustomFirebase.get_coach_email(du.email) + CustomFirebase.get_participants_email(du.email)))
                        if len(list_emails) > 0:
                            print(list_emails)
                            SendGrid.send_notification_coach(du.user_name, list_emails)
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
            if value.lower() in ["masculino", "male"]:
                self.update_data_user(param, 1)
            elif value.lower() == ["femenino", "female"]:
                self.update_data_user(param, 2)
        elif param == "emotion_neg":
            value = ''.join([i for i in value.lower() if i in string.ascii_lowercase]).strip()
            if value.lower() in ["triste", "sad"]:
                self.update_data_user(param, 2)
            elif value.lower() in ["frustrado", "frustrated"]:
                self.update_data_user(param, 1)
            elif value.lower() in ["irritado", "irritated"]:
                self.update_data_user(param, 3)

    def validate_data_daily_emotion(self, param, value, chat):
        # print(Fore.GREEN, param)
        # print(Fore.GREEN, value)
        if param == "emotion_neg":
            # We try to get the previous name intent and validate whit this.
            type_intent_previous = self.get_output_context(self.request.data['queryResult'])
            if type_intent_previous == 'i_starting_day-followup':
                chat = 1
            elif type_intent_previous in ['i_first_checkin-followup', 'i_starting_day_describe_problem-followup']:
                chat = 2
            value = ''.join([i for i in value.lower() if i in string.ascii_lowercase]).strip()
            print(param)
            print(value)
            if value.lower() in ["triste", "sad"]:
                self.create_emotion(param, 4, chat)
            elif value.lower() in ["frustrado", "frustrated"]:
                self.create_emotion(param, 3, chat)
            elif value.lower() in ["irritado", "irritated"]:
                self.create_emotion(param, 5, chat)
        elif param == "emotions_pos":
            value = ''.join([i for i in value.lower() if i in string.ascii_lowercase]).strip()
            if value.lower() in ["feliz", "happy"]:
                self.create_emotion(param, 1, chat)
            elif value.lower() in ["emocionado", "excited"]:
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
            return Response(data={'text': 'User doesn\'t exists'}, status=status.HTTP_400_BAD_REQUEST)
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
        work_taste = None
        print(work_taste)
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
                    print('Es false')
                    work_taste = False
                if daily.emotions_pos in [DailyEmotions.EMOTION.emotion_happy, DailyEmotions.EMOTION.emotion_excited]:
                    print('Es true')
                    work_taste = True
        print(work_taste)
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


class WeekMonthAPIView(APIView):

    def get(self, request):

        data = {
            'happy': 0,
            'excited': 0,
            'frustrated': 0,
            'sad': 0,
            'irritated': 0,
            'alerts_monday': 0,
            'alerts_tuesday': 0,
            'alerts_wednesday': 0,
            'alerts_thursday': 0,
            'alerts_friday': 0,
            'alerts_saturday': 0,
            'alerts_sunday': 0,
            'work_opinions': []
        }

        email = self.request.query_params.get('email')
        month = self.request.query_params.get('month')
        week = self.request.query_params.get('week')
        year = self.request.query_params.get('year')
        data_user = DataUser.objects.get(email=email)
        queryset = DailyEmotions.objects.filter(slack=data_user.slack)
        if month and year:
            month = int(month)
            year = int(year)
            queryset = queryset.filter(created__month=month,flow=DailyEmotions.FLOW.second_check_in)
            weeks = []
            for num_week, curent_week in enumerate(calendar.monthcalendar(year, month), 1):
                curent_week = list(filter(lambda x: x > 0, curent_week))
                start_day = f'{year}-{month}-{curent_week[0]}'
                end_day = f'{year}-{month}-{curent_week[len(curent_week) - 1]}'
                queryset_week = queryset.filter(created__range=(start_day,end_day))
                alerts = 0
                for daily_emotion in queryset_week:
                    alerts += int(daily_emotion.alerts_critical) + int(
                        daily_emotion.alerts_non_critical) + int(daily_emotion.alerts_total)
                #print(queryset_week.count())
                weeks.append({
                    'week': num_week,
                    'alerts':alerts
                })
                # print(f'Num week: {num_week}')
                # print(list(filter(lambda x: x > 0, curent_week)))
            data['weeks'] = weeks
        if week:
            queryset = queryset.filter(created__week=week)
            date = queryset.last().created
            start_day = date - datetime.timedelta(days=date.weekday())
            end_day = start_day + datetime.timedelta(days=6)
            data['start_week'] = start_day.date()
            data['end_week'] = end_day.date()
            queryset_alerts = queryset.filter(flow=DailyEmotions.FLOW.second_check_in)
            for daily_emotion_alerts in queryset_alerts:
                # print(daily_emotion_alerts.created)
                # print(daily_emotion_alerts.created.date().weekday())
                alerts_total = int(daily_emotion_alerts.alerts_critical) + int(
                    daily_emotion_alerts.alerts_non_critical) + int(daily_emotion_alerts.alerts_total)
                if daily_emotion_alerts.created.date().weekday() == 0:
                    data['alerts_monday'] = alerts_total
                elif daily_emotion_alerts.created.date().weekday() == 1:
                    data['alerts_tuesday'] = alerts_total
                elif daily_emotion_alerts.created.date().weekday() == 2:
                    data['alerts_wednesday'] = alerts_total
                elif daily_emotion_alerts.created.date().weekday() == 3:
                    data['alerts_thursday'] = alerts_total
                elif daily_emotion_alerts.created.date().weekday() == 4:
                    data['alerts_friday'] = alerts_total
                elif daily_emotion_alerts.created.date().weekday() == 5:
                    data['alerts_saturday'] = alerts_total
                elif daily_emotion_alerts.created.date().weekday() == 6:
                    data['alerts_sunday'] = alerts_total
            # print(queryset.count())

        for daily_emotion in queryset:
            #
            if daily_emotion.emotions_pos:
                if daily_emotion.emotions_pos == 1:
                    data['happy'] += 1
                elif daily_emotion.emotions_pos == 2:
                    data['excited'] += 1
            if daily_emotion.emotion_neg:
                if daily_emotion.emotion_neg == 3:
                    data['frustrated'] += 1
                elif daily_emotion.emotion_neg == 4:
                    data['sad'] += 1
                elif daily_emotion.emotion_neg == 5:
                    data['irritated'] += 1
            #
            if isinstance(daily_emotion.initial_change, str):
                data['work_opinions'].append(daily_emotion.initial_change)
            if isinstance(daily_emotion.first_problem, str):
                data['work_opinions'].append(daily_emotion.first_problem)
            if isinstance(daily_emotion.second_dislike, str):
                data['work_opinions'].append(daily_emotion.second_dislike)

        return Response(data=data, status=status.HTTP_200_OK)
