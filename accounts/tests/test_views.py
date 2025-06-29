from django.urls import reverse
from django.test import override_settings, TestCase
from django.utils.timezone import timedelta, datetime
from django.http import HttpResponse
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch
from freezegun import freeze_time

from accounts.models import User


class APITestCase(TestCase):
    client_class = APIClient
    
    def login(self, user):
        self.refresh = RefreshToken.for_user(user)
        
        response = HttpResponse()
        
        self.client.cookies['access_token'] = str(self.refresh.access_token)
        self.client.cookies['refresh_token'] = str(self.refresh)
        
        response.set_cookie(
            'access_token',
            str(self.refresh.access_token),
            httponly=True
        )
        response.set_cookie(
            'refresh_token',
            str(self.refresh),
            httponly=True
        )
        
        return response
        
    def assert_bad_request(self, response, expected_fields):
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for field in expected_fields:
            self.assertIn(field, response.data)


class TestRequestOTPView(APITestCase):
    @classmethod
    def setUpTestData(self):
        self.valid_phone = "+989123456789"
        self.valid_new_phone = "+989123456780"
        self.url = reverse('request-otp')
        self.user = User.objects.create(phone=self.valid_phone)
    
    def setUp(self):
        cache.clear()
        
    @override_settings(DEBUG=True)
    @patch('accounts.views.generate_otp_auth_num')
    @patch('accounts.views.send_otp_to_phone_tasks.delay')
    def test_request_otp_success_existing_user(self, mock_send_otp, mock_generate_otp):
        mock_generate_otp.return_value = "123456"

        response = self.client.post(self.url, {"phone": self.valid_phone})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["created"])
        self.assertEqual(response.data['otp'], '123456')
        
        mock_generate_otp.assert_called_once_with(self.valid_phone)
        mock_send_otp.assert_called_once_with("123456")
    
    @override_settings(DEBUG=True)
    @patch('accounts.views.generate_otp_auth_num')
    @patch('accounts.views.send_otp_to_phone_tasks.delay')
    def test_request_otp_success_new_user(self, mock_send_otp, mock_generate_otp):
        mock_generate_otp.return_value = "123456"

        response = self.client.post(self.url, {"phone": self.valid_new_phone})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["created"])
        self.assertEqual(response.data['otp'], '123456')
        
        mock_generate_otp.assert_called_once_with(self.valid_new_phone)
        mock_send_otp.assert_called_once_with("123456")

    @override_settings(DEBUG=True)
    @patch('accounts.views.generate_otp_auth_num')
    @patch('accounts.views.send_otp_to_phone_tasks.delay')
    def test_invalid_phone_format(self, mock_send_otp, mock_generate_otp):
        response = self.client.post(self.url, {"phone": "invalid"}, format='json')
        
        self.assert_bad_request(response, ['phone'])
    
    def request_at(self, frozen_time):
        with freeze_time(frozen_time):
            return self.client.post(self.url, {'phone': self.valid_phone})
        
    @override_settings(
        CACHES={
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            }
        },
        OTP={
            "EXPIRATION_TIME_SECONDS": 120,
            "LONG_TIME_SECONDS": 2 * 60 * 60,
            "LONG_MAX_REQUESTS": 20,
            "VALID_WINDOW": 1,
        },
        DEBUG=False,
    )
    @patch('accounts.views.send_otp_to_phone_tasks.delay')
    @patch('accounts.views.generate_otp_auth_num')
    def test_throttling_protection(self, mock_generate_otp, mock_send_otp):
        mock_generate_otp.return_value = '111111'
        start_time = datetime(2025, 1, 1, 12, 0, 0)
        
        for i in range(20):
            response = self.request_at(start_time + timedelta(minutes=i))   
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        
        response = self.request_at(start_time + timedelta(hours=2, seconds=1))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        response = self.request_at(start_time + timedelta(hours=2, seconds=2))
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        
        for i in range(2):
            response = self.client.post(self.url, {'phone': self.valid_phone})   
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


class TestVerifyOTPView(APITestCase):
    @classmethod
    def setUpTestData(self):
        self.valid_phone = "+989123456789"
        self.valid_new_phone = "+989123456780"
        self.url = reverse('verify-otp')
        self.user = User.objects.create(phone=self.valid_phone)
    
    @override_settings(DEBUG=True)
    @patch('accounts.serializers.verify_otp_auth_num', return_value=True)
    def test_success_existing_user(self, mock_verify_otp):
        response = self.client.post(self.url, {"phone": self.valid_phone, "otp": 123456})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["phone"], self.valid_phone)
        self.assertFalse(response.data['created'])
        self.assertIn('access_token', response.cookies.keys())
        self.assertIn('refresh_token', response.cookies.keys())
        mock_verify_otp.assert_called_once_with(self.valid_phone, 123456)
    
    @override_settings(DEBUG=True)
    @patch('accounts.serializers.verify_otp_auth_num', return_value=True)
    def test_success_new_user(self, mock_verify_otp):
        response = self.client.post(self.url, {"phone": self.valid_new_phone, "otp": 123456})
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["phone"], self.valid_new_phone)
        self.assertTrue(response.data['created'])
        self.assertIn('access_token', response.cookies.keys())
        self.assertIn('refresh_token', response.cookies.keys())
        mock_verify_otp.assert_called_once_with(self.valid_new_phone, 123456)
        
    @override_settings(DEBUG=True)
    @patch('accounts.serializers.verify_otp_auth_num', return_value=False)
    def test_otp_invalid(self, mock_verify_otp):
        response = self.client.post(self.url, {"phone": self.valid_phone, "otp": 123456})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('access_token', response.cookies.keys())
        self.assertNotIn('refresh_token', response.cookies.keys())
        mock_verify_otp.assert_called_once_with(self.valid_phone, 123456)

    def test_missing_otp(self):
        response = self.client.post(self.url, {"phone": self.valid_phone})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('access_token', response.cookies.keys())
        self.assertNotIn('refresh_token', response.cookies.keys())
    
    def test_invalid_phone(self):
        response = self.client.post(self.url, {"phone": "invalid", "otp": 123456})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('access_token', response.cookies.keys())
        self.assertNotIn('refresh_token', response.cookies.keys())
    
    def test_missing_phone(self):
        response = self.client.post(self.url, {"otp": 123456})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('access_token', response.cookies.keys())
        self.assertNotIn('refresh_token', response.cookies.keys())


class TestLogoutView(APITestCase):
    def setUp(self):
        self.url_logout = reverse('logout')
        self.user = User.objects.create(phone="+989123456789")
        
    def test_logout_success(self):
        self.login(self.user)
        
        self.assertIn('access_token', self.client.cookies.keys())
        response = self.client.post(self.url_logout)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.cookies['access_token'].value, "")
        self.assertEqual(response.cookies['refresh_token'].value, "")
    
    def test_logout_without_login(self):
        response = self.client.post(self.url_logout)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access_token', response.cookies.keys())
        self.assertNotIn('refresh_token', response.cookies.keys())


class TestRefreshTokenView(APITestCase):
    @classmethod
    def setUpTestData(self):
        self.url = reverse('token-refresh')
        self.user = User.objects.create(phone="+989123456789")
        self.user.save()
        
    def test_refresh_token_success(self):
        response_login = self.login(self.user)
        self.assertIn('access_token', self.client.cookies.keys())
        self.assertIn('access_token', self.client.cookies.keys())
        
        response_refresh = self.client.post(self.url)
        self.assertEqual(response_refresh.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', self.client.cookies.keys())
        self.assertIn('refresh_token', self.client.cookies.keys())
        
        self.assertNotEqual(self.client.cookies['access_token'].value, response_login.cookies['access_token'].value)
        self.assertEqual(self.client.cookies['refresh_token'].value, response_login.cookies['refresh_token'].value)
    
    def test_refresh_token_without_login(self):
        response = self.client.post(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertNotIn('access_token', response.cookies.keys())
        self.assertNotIn('refresh_token', response.cookies.keys())


class TestChangePhoneRequestView(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.valid_phone = "+989123456789"
        cls.valid_new_phone = "+989123456780"
        cls.url = reverse('change-phone-request')
        cls.user = User.objects.create(phone=cls.valid_phone)
    
    def setUp(self):
        self.login(self.user)
    
    @override_settings(DEBUG=True)
    @patch('accounts.views.generate_otp_change_phone', return_value=123456)
    @patch('accounts.views.send_otp_to_phone_tasks.delay')
    def test_request_otp_success(self, mock_send_otp, mock_generate_otp):
        response = self.client.post(self.url, {"phone": self.valid_new_phone})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['otp'], 123456)
        
        mock_generate_otp.assert_called_once_with(self.valid_new_phone)
        mock_send_otp.assert_called_once_with(123456)
    
    def test_request_otp_without_login(self):
        self.client.cookies['access_token'] = 'invalid.token.here'
        response = self.client.post(self.url, {"phone": self.valid_new_phone})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('otp', response.data)
    
    def test_request_otp_invalid_phone(self):
        response = self.client.post(self.url, {"phone": "invalid"})
        self.assert_bad_request(response, ["phone"])
    
    def test_request_otp_missing_phone(self):
        response = self.client.post(self.url, {})
        self.assert_bad_request(response, ["phone"])
    
    def test_request_otp_phone_already_exists(self):
        User.objects.create(phone=self.valid_new_phone)
        response = self.client.post(self.url, {"phone": self.valid_new_phone})
        self.assert_bad_request(response, ["phone"])


class TestChangePhoneVerifyView(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.valid_phone = "+989123456789"
        cls.valid_new_phone = "+989123456780"
        cls.url = reverse('change-phone-verify')
        cls.user = User.objects.create(phone=cls.valid_phone)
    
    def setUp(self):
        self.login(self.user)
    
    @override_settings(DEBUG=True)
    @patch('accounts.serializers.verify_otp_change_phone', return_value=True)
    def test_verify_otp_success(self, mock_verify_otp):
        response = self.client.post(self.url, {"phone": self.valid_new_phone, "otp": 123456})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_verify_otp.assert_called_once_with(self.valid_new_phone, 123456)
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone, self.valid_new_phone)
        
    def test_verify_otp_without_login(self):
        self.client.cookies['access_token'] = 'invalid.token.here'
        response = self.client.post(self.url, {"phone": self.valid_new_phone, "otp": 123456})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('phone', response.data)
    
    @patch('accounts.serializers.verify_otp_change_phone', return_value=True)
    def test_verify_otp_invalid_phone(self, mock_verify_otp):
        response = self.client.post(self.url, {"phone": "invalid", "otp": 123456})
        self.assert_bad_request(response, ["phone"])
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone, self.valid_phone)
    
    @patch('accounts.serializers.verify_otp_change_phone', return_value=True)
    def test_verify_otp_missing_phone(self, mock_verify_otp):
        response = self.client.post(self.url, {"otp": 123456})
        self.assert_bad_request(response, ["phone"])
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone, self.valid_phone)
    
    @patch('accounts.serializers.verify_otp_change_phone', return_value=True)
    def test_verify_otp_missing_otp(self, mock_verify_otp):
        response = self.client.post(self.url, {"phone": self.valid_new_phone})
        self.assert_bad_request(response, ["otp"])
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone, self.valid_phone)
    
    @patch('accounts.serializers.verify_otp_change_phone', return_value=True)
    def test_verify_otp_phone_already_exists(self, mock_verify_otp):
        User.objects.create(phone=self.valid_new_phone)
        response = self.client.post(self.url, {"phone": self.valid_new_phone, "otp": 123456})
        self.assert_bad_request(response, ["phone"])
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone, self.valid_phone)
    
    @patch('accounts.serializers.verify_otp_change_phone', return_value=False)
    def test_invalid_otp(self, mock_verify_otp):
        response = self.client.post(self.url, {"phone": self.valid_new_phone, "otp": 000000})
        self.assert_bad_request(response, ["otp"])
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone, self.valid_phone)
        mock_verify_otp.assert_called_once_with(self.valid_new_phone, 000000)
