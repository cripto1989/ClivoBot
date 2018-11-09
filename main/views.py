from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class test(APIView):

    def post(self, request, format=None):
        return Response(data={},status=status.HTTP_200_OK)

    
