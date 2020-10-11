from django.test import TestCase
from django.test import Client

from .models import BlockingModel, ChatModel, EventLogModel, LogModel
from userauth.models import UserModel
from . import erros_types 
from . import user_events 
from .models import LogModel
from django.db.models import Q



class ErrorEventsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        
    def test_not_authenticated_event(self):
        response = self.client.post('/api/v1/login/', {})
        self.assertEqual(response.status_code, 401)
        try:
            err = LogModel.objects.get(error_message=erros_types.NOT_AUTHENTICATED)
            self.assertIsNotNone(err)
        except LogModel.DoesNotExist:
            self.assertIsNotNone(None)
    
    def test_wrong_password_event(self):
        UserModel(username='user', password='password', email='email').save()
        response = self.client.post('/api/v1/login/', {"username":"user", "password":"false_password","email":"email"})
        self.assertEqual(response.status_code, 401)
        try:
            err = LogModel.objects.get(error_message=erros_types.WRONG_PASSWORD)
            self.assertIsNotNone(err)
        except LogModel.DoesNotExist:
            self.assertIsNotNone(None)
    
    def test_user_exists_event(self):
        UserModel(username='user', password='password', email='email').save()
        response = self.client.post('/api/v1/register/', {"username":"user", "password":"password","email":"email"})
        self.assertEqual(response.status_code, 400)
        try:
            err = LogModel.objects.get(error_message=erros_types.USER_ALREADY_EXISTS)
            self.assertIsNotNone(err)
        except LogModel.DoesNotExist:
            self.assertIsNotNone(None)
    
    def test_repeated_blocking_event(self):
        user = UserModel(username='user', password='password', email='email')
        user2 = UserModel(username='user2', password='password', email='email2')
        token = user.token
        user.save()
        user2.save()
        response = self.client.post('/api/v1/block/user/?username=user2', {"token":token})
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/api/v1/block/user/?username=user2', {"token":token})
        self.assertEqual(response.status_code, 404)
        try:
            err = LogModel.objects.get(error_message=erros_types.REPEATED_BLOCKING_ATTEMPT)
            self.assertIsNotNone(err)
        except LogModel.DoesNotExist:
            self.assertIsNotNone(None)

    def test_shows_history_event(self):
        user = UserModel(username='user', password='password', email='email')
        user2 = UserModel(username='user2', password='password', email='email2')
        token = user.token
        user.save()
        user2.save()        
        response = self.client.post('/api/v1/chat/history/?username=user3', {"token":token})
        self.assertEqual(response.status_code, 404)
        try:
            err = LogModel.objects.get(error_message=erros_types.USER_NOT_FOUND)
            self.assertIsNotNone(err)
        except LogModel.DoesNotExist:
            self.assertIsNotNone(None)

            


class UnAuthTestCase(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_unauthenticated_requests(self):
        """unauthenticated requests returns 401"""

        response = self.client.post('/api/v1/login/', {})
        self.assertEqual(response.status_code, 401)

        response = self.client.post('/api/v1/register/', {})
        self.assertEqual(response.status_code, 401)

        response = self.client.post('/api/v1/chat/history/', {})
        self.assertEqual(response.status_code, 401)

        response = self.client.post('/api/v1/contacts/all/', {})
        self.assertEqual(response.status_code, 401)

        response = self.client.post('/api/v1/chat/last_messages/', {})
        self.assertEqual(response.status_code, 401)

        response = self.client.post('/api/v1/block/user/', {})
        self.assertEqual(response.status_code, 401)

        response = self.client.post('/api/v1/unblock/user/', {})
        self.assertEqual(response.status_code, 401)

        response = self.client.post('/api/v1/send_message/', {})
        self.assertEqual(response.status_code, 401)

# Create your tests here.
class ChatModelTestCase(TestCase):
    def setUp(self):
        self.furkan = UserModel.objects.create(username='furkan', password='password', email='furkan@hotmail.com')
        self.osman = UserModel.objects.create(username='osman', password='password', email='osman@hotmail.com')
        ChatModel.objects.create(sender=self.furkan, reciever=self.osman, message='hello osman')
        ChatModel.objects.create(sender=self.osman, reciever=self.furkan, message='hello furkan')

    def test_unread_messages_are_not_seen(self):
        """ unread messages are set to not seen """
        messages = ChatModel.objects.filter(Q(sender=self.furkan) | Q(sender=self.osman))
        for message in messages:
            self.assertEqual(message.seen, False)
        
    def test_chat_models_are_not_null(self):
        """ chats messages created """
        furkan_to_osman = ChatModel.objects.filter(message="hello osman")[0]
        osman_to_furkan = ChatModel.objects.filter(message="hello furkan")[0]
        self.assertEqual(furkan_to_osman.is_exists(), True)
        self.assertEqual(osman_to_furkan.is_exists(), True)

    def test_users_can_send_messages_to_each_other(self):
        """senders and recievers are set correctly"""
        furkan_to_osman = ChatModel.objects.filter(message="hello osman")[0]
        osman_to_furkan = ChatModel.objects.filter(message="hello furkan")[0]
        self.assertEqual(furkan_to_osman.sender.pk, self.furkan.pk)
        self.assertEqual(osman_to_furkan.sender.pk, self.osman.pk)
        self.assertEqual(furkan_to_osman.reciever.pk, self.osman.pk)
        self.assertEqual(osman_to_furkan.reciever.pk, self.furkan.pk)
