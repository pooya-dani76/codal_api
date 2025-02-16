from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from .codal import codalWebScraping
from selenium.common.exceptions import TimeoutException

# Create your views here.


class ProcessDataApiView(APIView):
    def get(self, request: Request):
        return Response({"message": "test-request works correctly!",}, status=status.HTTP_200_OK)

    def post(self, request: Request):
        data = request.data

        page = data.get('page')
        if page == None:
            page = 1

        length = data.get('length')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        try:
            start_year = int(start_date.get('year'))
            start_month = int(start_date.get('month'))
            start_day = int(start_date.get('day'))

            end_year = int(end_date.get('year'))
            end_month = int(end_date.get('month'))
            end_day = int(end_date.get('day'))
        except:
            return Response({"message": "start or end date format is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

        if length == None:
            return Response({"message": "length is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            length = int(length)
        except:
            return Response({"message": "length should be an integer as string"}, status=status.HTTP_400_BAD_REQUEST)

        if start_year == None or start_month == None or start_day == None:
            return Response({"message": "start date is invalid"}, status=status.HTTP_400_BAD_REQUEST)

        if end_year == None or end_month == None or end_day == None:
            return Response({"message": "end date is invalid"}, status=status.HTTP_400_BAD_REQUEST)

        new: codalWebScraping = codalWebScraping()
        try:
            output = new.noon_30_per_page(
            {"year": start_year, "month": start_month, "day": start_day},
            {"year": end_year, "month": end_month, "day": end_day},
            length=length,
            current_page_number=page)
            return Response({"data": output}, status=status.HTTP_200_OK)
        except TimeoutException:
            return Response({"message": "connection to codal failed"}, status=status.HTTP_504_GATEWAY_TIMEOUT)
        
