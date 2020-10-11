from django.test import TestCase
from django.test import Client

from .models import UserModel

# Create your tests here.
class LoginRegisterTestCase(TestCase):
    """login and register works"""
    def setUp(self):
        self.client = Client()
        UserModel(username='test_user', password='password', email='test@hotmail.com').save()

    def test_login(self):
        """user can login with correct user name and password"""
        response = self.client.post('/api/v1/login/', {"username":"test_user", "password":"password"})
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data['token'])
        self.assertIsNotNone(response.data['expiration_date'])

    def test_false_login(self):
        """user can not login with false user name nad password"""
        response = self.client.post('/api/v1/login/', {"username":"test_user", "password":"false_password"})
        self.assertEqual(response.status_code, 401)

    def test_register(self):
        """user can register"""
        response = self.client.post('/api/v1/register/', {"username":"new_test_user", "password":"password", "email":"newtest@hotmail.com"})
        self.assertEqual(response.status_code, 200)

    def test_same_username_can_not_register_again(self):
       
        response = self.client.post('/api/v1/register/', {"username":"new_test_user", "password":"password", "email":"diff@hotmail.com"})
        self.assertEqual(response.status_code, 200) 

        response = self.client.post('/api/v1/register/', {"username":"new_test_user", "password":"password", "email":"newtest@hotmail.com"})
        self.assertEqual(response.status_code, 400) 

    def test_register_with_missing_data_should_fail(self):
        """user can not registef if the proviede credetials are missing or false"""
        response = self.client.post('/api/v1/register/', {"username":"new_test_user", "password":"password" })
        self.assertEqual(response.status_code, 401)
        
        response = self.client.post('/api/v1/register/', { "password":"password", "email":"newtest@hotmail.com" })
        self.assertEqual(response.status_code, 401)

        response = self.client.post('/api/v1/register/', { "user":"new_test_user", "password":"password", "email":"newtest@hotmail.com" })
        self.assertEqual(response.status_code, 401)

