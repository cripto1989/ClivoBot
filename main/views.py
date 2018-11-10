import json

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from colorama import Fore, init

from main.models import History

init()


class CallBackAPIView(APIView):
    INTENTS= [
        {
            'intent': '',
            'param': ''
        }
    ]

    def post(self, request, format=None):
        print(Fore.GREEN + json.dumps(self.request.data))
        session = self.request.data['session']
        self.save_json(self.request.data, session)
        return Response(data={}, status=status.HTTP_200_OK)

    def validate_data(self):
        pass

    def save_json(self, json_data, session):
        History.objects.create(
            data=json_data, session=session
        )
