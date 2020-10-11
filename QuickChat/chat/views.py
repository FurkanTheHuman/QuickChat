from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import generics
from .models import ChatModel, BlockingModel, LogModel
from userauth.models import UserModel
from .serializers import ChatSerializer
from rest_framework import permissions
from userauth.models import UserModel
import pytz
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
from django.db.models import Q
from . import erros_types
from . import user_events
from .erros_types import log_error
from .user_events import log_event
from django.utils.datastructures import MultiValueDictKeyError


def verify_token(user_object, request): # Could be a decorator
    if user_object.expiration_date < datetime.utcnow().replace(tzinfo=pytz.utc):
        log_error(error_message=erros_types.TOKEN_EXPIRED, location="verify_token", responsible_user=user_object)
        return False
    if str(user_object.token) != request.data['token']:
        log_error(error_message=erros_types.WRONG_TOKEN, location="verify_token", responsible_user=user_object)    
        return False
    log_event(user_events.TOKEN_VERFIED, user=user_object)
    return True

def update_session(user_object):
    user_object.expiration_date = datetime.utcnow().replace(tzinfo=pytz.utc) + timedelta(days=1)
    user_object.save()
    log_event(user_events.SESSION_UPDATE, user=user_object)



def get_object(username):
    try:
        return UserModel.objects.get(username=username)
    except UserModel.DoesNotExist:
        return False



class SendMessage(APIView):

    def post(self, request):
        try:
            reciever = get_object(request.data['reciever'])
            sender = get_object(request.data['sender'])
            message = request.data['message']
            update_session(sender)
        except (MultiValueDictKeyError, KeyError):
            return Response({"error":"not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
        if sender == False or reciever == False:
            return Response({"error":"reciever does not exist"}, status=status.HTTP_404_NOT_FOUND)
        if BlockingModel.objects.filter(username=reciever, blocked_user=sender).count() > 0:
            return Response({"error":"you are blocked"}, status=status.HTTP_200_OK)
        if verify_token(sender,request) : 
            chat = ChatModel(sender=sender, reciever=reciever, message=message)
            chat.save()
            log_event(user_events.SEND_MESSAGE, user=sender)
            return Response({"state":"success"}, status=status.HTTP_200_OK)
        log_error(error_message=erros_types.NOT_AUTHENTICATED, location="SendMessage")
        return Response({"error":"not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)


class LastMessages(APIView):

    def post(self, request):
        try:
            user = get_object(request.data['username'])
            update_session(user)
        except (MultiValueDictKeyError, KeyError):
            return Response({"error":"not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
            
        if verify_token(user,request) : 
            chat = ChatModel.objects.filter(reciever=user)
            val = chat.order_by().values('sender').distinct()
            last_messages = []
            for i in val:
                print(i) 
                filtered = ChatModel.objects.filter(sender=UserModel.objects.get(pk=i['sender']), reciever=user, seen=False).order_by('-send_date')
                try:
                    message = filtered[0].message
                except IndexError:
                    message = 'empty'
                last_messages.append({"sender": UserModel.objects.get(pk=i['sender']).username, "count":filtered.count(), "message":message })
            

            log_event(user_events.SEND_MESSAGE)
            return Response(last_messages, status=status.HTTP_200_OK)
        log_error(error_message=erros_types.NOT_AUTHENTICATED, location="SendMessage")
        return Response({"error":"not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

class ChatHistory(APIView):
   
    def post(self, request):
        try:
            friend = get_object(request.GET.get('username', ''))
            user = UserModel.objects.get(token=request.data['token'])
            update_session(user)
        except (MultiValueDictKeyError, KeyError):
            return Response({"error":"not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
            
        if verify_token(user, request) and friend is not False: 
            chat = ChatModel.objects.filter(
                Q(sender=user.pk, reciever=friend.pk ) | 
                Q(sender=friend.pk , reciever=user.pk )).order_by('-send_date')
            for message in chat:
                if message.sender.pk == friend.pk:
                    message.seen = True
                    message.save()
            serial = ChatSerializer(chat, many=True)
            log_event(user_events.SHOW_MESSAGES, user=user)
            return Response({"chats":serial.data}, status=status.HTTP_200_OK)

        if friend is False:
            log_error(error_message=erros_types.USER_NOT_FOUND, location="ChatHistory", responsible_user=user)
            return Response({"error":"user not found"}, status=status.HTTP_404_NOT_FOUND)
        log_error(error_message=erros_types.NOT_AUTHENTICATED, location="BlockUser")
        return Response({"error":"not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)


class BlockUser(APIView):
    def post(self, request, unblock=False):
        try:
            blocked = get_object(request.GET.get('username', ''))
            blocker = UserModel.objects.get(token=request.data['token'])

        except (MultiValueDictKeyError, KeyError):
            return Response({"error":"not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
                        
        # blocker.expiration_date = datetime.utcnow().replace(tzinfo=pytz.utc) + timedelta(days=1)
        update_session(blocker)
        if verify_token(blocker, request) and blocked is not False: 
            block = BlockingModel(blocked_user=blocked, username=blocker)
            
            if unblock == True:
                name = blocked.username
                block_list = BlockingModel.objects.filter(blocked_user=blocked, username=blocker)
                if block_list.count() == 0:
                    log_error(error_message=erros_types.REPEATED_UNBLOCKING_ATTEMPT, location="BlockUser", responsible_user=blocker)
                    return Response({"error":str(name)+" is already unblocked"}, status=status.HTTP_404_NOT_FOUND)

                for b in BlockingModel.objects.filter(blocked_user=blocked, username=blocker):    
                    b.self_terminate()

                log_event(user_events.UNBLOCK_USER, user=blocker)
                return Response({"state":str(name)+" is  unblocked"}, status=status.HTTP_200_OK)

            if block.is_blocked():
                log_error(error_message=erros_types.REPEATED_BLOCKING_ATTEMPT, location="BlockUser", responsible_user=blocker)
                return Response({"error":str(blocked)+" is already blocked"}, status=status.HTTP_404_NOT_FOUND)
            block.save()

            log_event(user_events.BLOCK_USER, user=blocker)
            return Response({"state":str(blocked)+" is blocked"}, status=status.HTTP_200_OK)

        if blocked is False:
            log_error(error_message=erros_types.USER_NOT_FOUND, location="BlockUser", responsible_user=blocker)
            return Response({"error":"user not found"}, status=status.HTTP_404_NOT_FOUND)

        log_error(error_message=erros_types.NOT_AUTHENTICATED, location="BlockUser")
        return Response({"error":"not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)

class UnBlockUser(APIView):
    def post(self, request):
        return BlockUser.post(self, request, unblock=True)