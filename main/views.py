import json

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from colorama import Fore, init

init()


class test(APIView):

    def post(self, request, format=None):
        # print(json.dumps(self.request.data))
        print(Fore.GREEN + json.dumps(self.request.data))
        data = {
        }
        return Response(data=data, status=status.HTTP_200_OK)

    def validate_data(self):
        """
        Here we have to validate if the data is in request.data
        :return:
        """
        pass

    def save_json(self):
        """
        Here we need to save the history
        :return:
        """
        pass
