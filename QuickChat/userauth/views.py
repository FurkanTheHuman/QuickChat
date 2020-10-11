from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import UserModel
from .serializers import UserSerializer, UserNameSerializer
from django.http import Http404
from django.http import JsonResponse
# Create your views here.
import json
from rest_framework.parsers import JSONParser
from django.db.utils import IntegrityError
from datetime import datetime, timedelta
import uuid
import pytz
from rest_framework import generics
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from chat.erros_types import log_error
from chat.user_events import log_event
from chat import erros_types
from chat import user_events


from django.utils.datastructures import MultiValueDictKeyError

class CreateUser(APIView):
    
    def get_object(self, username):
        try:
            return UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            return False
    
    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        usernames = UserModel.objects.all()
        res = UserSerializer(usernames, many=True)
        log_event(user_events.LIST_USERS, user=None)
        return JsonResponse(res.data, safe=False)

    def post(self, request):
        try:
            user = self.get_object(request.data['username'])
        except (MultiValueDictKeyError, KeyError):
            return Response({"error":"not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        if not user :
            try:
                req = request.data
                email = req['email']
                username = req['username']
                password = req['password']
            except (MultiValueDictKeyError, KeyError):
                return Response({"error":"not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
            try:
                userlog = UserModel(username=username, email=email, password=password)
                userlog.save()
                log_event(user_events.REGISTER, user=userlog)
            except IntegrityError:
                log_error(error_message=erros_types.USER_ALREADY_EXISTS, location="CreateUser")
                return Response({"error":"user already exists"}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"state":"success","token":(userlog.token) ,"data":request.data})  
        log_error(error_message=erros_types.USER_ALREADY_EXISTS, location="CreateUser")
        return Response({"error":"user already exists"}, status=status.HTTP_400_BAD_REQUEST)

class LoginUser(APIView):
    
    def get_object(self, username):
        try:
            return UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            return False
    
    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        usernames = UserModel.objects.all()
        res = UserSerializer(usernames, many=True)
        return JsonResponse(res.data, safe=False)

    def post(self, request):
        try:
            user = self.get_object(request.data['username'])
            password = request.data['password']
        except (MultiValueDictKeyError, KeyError):
            log_error(error_message=erros_types.NOT_AUTHENTICATED, location="LoginUser")
            return Response({"error":"not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

        if user is False : 
            log_error(error_message=erros_types.NOT_AUTHENTICATED, location="LoginUser")
            return Response({"error":"not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        if password != user.password:
            log_error(error_message=erros_types.WRONG_PASSWORD, location="LoginUser")
            return Response({"error":"wrong password"}, status=status.HTTP_401_UNAUTHORIZED)

        # for timezone error to disappear
        user.expiration_date = datetime.utcnow().replace(tzinfo=pytz.utc) + timedelta(days=1)
        user.save()
        log_event(user_events.LOGIN, user=user)
        return Response({"token": user.token, "expiration_date": user.expiration_date})



class ListUsers(APIView):
    
    def get_object(self, username):
        try:
            return UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            return False

    def post(self, request):
        try:
            # user = self.get_object(request.data['username'])
            user = UserModel.objects.get(token=request.data['token'])
        except (MultiValueDictKeyError, KeyError):
            return Response({"error":"not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        if user is False : 
            log_error(error_message=erros_types.NOT_AUTHENTICATED, location="ListUsers")
            return Response({"error":"not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        # for timezone error to disappear
        user.expiration_date = datetime.utcnow().replace(tzinfo=pytz.utc) + timedelta(days=1)
        user.save()
        all = UserModel.objects.all()
        log_event(user_events.LIST_USERS, user=user)
        return Response({"users":UserNameSerializer(all, many=True).data})


