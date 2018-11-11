import datetime
import json

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from colorama import Fore, init

from main.models import History, DataUser

init()


class CallBackAPIView(APIView):
    INTENTS = [
        {
            'intent': 'i_welcome_ask_jobcoach_name',
            'param': 'user_name',
            'validate': False
        },
        {
            'intent': 'i_welcome_ask_user_email',
            'param': 'jobcoach_name',
            'validate': False
        },
        {
            'intent': 'i_welcome_ask_gender',
            'param': 'email',
            'validate': False
        },
        {
            'intent': 'i_welcome_ask_emotions',
            'param': 'user_gender',
            'validate': True
        },
        {
            'intent': 'i_welcome_jobcoach_contact_onboard',
            'param': 'emotion_neg',
            'validate': True
        }
    ]

    def post(self, request, format=None):
        # print(Fore.GREEN + json.dumps(self.request.data))
        session = self.request.data['session']
        self.save_json(self.request.data, session)

        if "queryResult" in self.request.data:
            if "intent" in self.request.data["queryResult"]:
                intent = self.request.data["queryResult"]["intent"]["displayName"]
                data_filter = list(filter(lambda dict_intent: dict_intent['intent'] == intent, self.INTENTS))
                if len(data_filter) > 0:
                    obj_dict = data_filter[0]
                    param = obj_dict['param']
                    validate = obj_dict['validate']
                    if "parameters" in self.request.data["queryResult"]:
                        value = self.request.data["queryResult"]["parameters"][param]
                        if validate:
                            self.validate_data(param, value)
                        else:
                            self.update_data_user(param, value)
        return Response(data={}, status=status.HTTP_200_OK)

    def get_or_create_data(self):
        today = datetime.date.today()
        obj, created = DataUser.objects.get_or_create(created__date=today,
                                             session_id=self.request.data['session'])
        return obj

    def update_data_user(self, parameter, value):
        print(Fore.RED, "Llego a crear")
        obj = self.get_or_create_data()
        DataUser.objects.filter(pk=obj.id).update(**{parameter: value})

    def validate_data(self, param, value):
        print(Fore.BLUE, value)
        if param == "user_gender":
            if value.lower() == "masculino":
                self.update_data_user(param, 1)
            elif value.lower == "femenino":
                self.update_data_user(param, 2)
        # elif param == "emotion_neg":
        #     pass

    def save_json(self, json_data, session):
        History.objects.create(
            data=json_data, session=session
        )
