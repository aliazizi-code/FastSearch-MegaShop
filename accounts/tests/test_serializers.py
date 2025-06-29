from django.test import TestCase
from rest_framework.exceptions import ValidationError
from unittest.mock import patch

from accounts.models import User
from accounts.serializers import (
    # Fields
    PhoneNumberField,
    
    # Serializers
    RequestOTPSerializer,
    VerifyOTPSerializer,
    ChangePhoneRequestSerializer,
    ChangePhoneVerifySerializer,
)


class TestPhoneNumberField(TestCase):
    def setUp(self):
        self.field = PhoneNumberField()
        
    def test_valid_phone_number(self):
        """Test valid phone number formats"""
        valid_numbers = [
            '+981234567890',
            '+989876543210',
        ]
        
        for number in valid_numbers:
            self.assertEqual(
                self.field.run_validation(number), number,
                f"Phone number {number} should be considered valid"
            )
    
    def test_invalid_phone_number(self):
        """Test invalid phone number formats"""
        
        invalid_numbers = [
            '989123456789',    # Missing +
            '+98123456789',    # Wrong prefix
            '+98912345678',    # Less than 12 digits
            '+9891234567890',  # More than 12 digits
            '+98912abc6789',   # Contains letters
            '09123456789',     # Old format
            '+98912 345 6789'  # Contains spaces
        ]
        
        for number in invalid_numbers:
            with self.assertRaises(ValidationError, msg=f"Phone number {number} should be considered invalid"):
                self.field.run_validation(number)


class TestRequestOTPSerializer(TestCase):
    def test_valid(self):
        valid_data = {'phone': '+989876543210'}
        serializer = RequestOTPSerializer(data=valid_data)
        self.assertTrue(serializer.is_valid())
        
    def test_invalid(self):
        invalid_data = [
            {'phone': ''},
            {'phone': '09876543210'},
            {'phone': 'invalid'},
            {'phone': '+12345678901234'},
        ]
        
        for data in invalid_data:
            serializer = RequestOTPSerializer(data=data)
            with self.assertRaises(ValidationError):
                serializer.is_valid(raise_exception=True)


class TestVerifyOTPSerializer(TestCase):
    def setUp(self):
        self.valid_data = {
            'phone': '+989123456789',
            'otp': 123456
        }
    
    @patch('accounts.serializers.verify_otp_auth_num')
    def test_valid_otp(self, mock_verify):
        """Test with valid OTP"""
        mock_verify.return_value = True
        
        serializer = VerifyOTPSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['otp'], 123456)
        self.assertEqual(serializer.validated_data['phone'], self.valid_data['phone'])
    
    @patch('accounts.serializers.verify_otp_auth_num')
    def test_invalid(self, mock_verify):
        """Test with invalid OTP"""
        mock_verify.return_value = False
        
        serializer = VerifyOTPSerializer(data=self.valid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('otp', serializer.errors)
        
    def test_missing_otp(self):
        """Test when OTP is missing"""
        invalid_data = {'phone': '+989123456789'}
        serializer = VerifyOTPSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('otp', serializer.errors)
        
    @patch('accounts.serializers.verify_otp_auth_num')
    def test_invalid_phone_formats(self, mock_verify):
        """Test various invalid phone number formats"""
        mock_verify.return_value = True
        invalid_cases = [
            {
                'description': 'Number with 0 prefix',
                'data': {'phone': '09123456789', 'otp': 123456},
            },
            {
                'description': 'Short length',
                'data': {'phone': '+989123456', 'otp': 123456},
            },
            {
                'description': 'Long length',
                'data': {'phone': '+9891234567890', 'otp': 123456},
            },
            {
                'description': 'No country code',
                'data': {'phone': '9123456789', 'otp': 123456},
            },
            {
                'description': 'Wrong country code',
                'data': {'phone': '+90123456789', 'otp': 123456},
            },
            {
                'description': 'Contains letters',
                'data': {'phone': '+98abc456789', 'otp': 123456},
            },
            {
                'description': 'Contains spaces',
                'data': {'phone': '+98 912 345 6789', 'otp': 123456},
            },
            {
                'description': 'Empty phone',
                'data': {'phone': '', 'otp': 123456},
            },
            {
                'description': 'Missing phone',
                'data': {'phone': None, 'otp': 123456},
            },
        ]

        for case in invalid_cases:
            description = case['description']
            with self.subTest(description):
                serializer = VerifyOTPSerializer(data=case['data'])
                self.assertFalse(serializer.is_valid(), f"Test failed for case: {description}")
                self.assertIn('phone', serializer.errors, f"Phone error missing for case: {description}")


class TestChangePhoneRequestSerializer(TestCase):
    def setUp(self):
        self.user = User.objects.create(phone='+989123456789')
    
    def test_validate_phone(self):
        serializer = ChangePhoneRequestSerializer(data={'phone': '+989123456789'})
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('phone', serializer.errors)


class TestChangePhoneVerifySerializer(TestCase):
    
    @patch('accounts.serializers.verify_otp_change_phone')
    def test_validate_otp(self, mock_verify_otp):
        self.user = User.objects.create(phone='+989123456789')
        mock_verify_otp.return_value = False
        data = {
            'phone': '+989123456789',
            'otp': 'wrong_code'
        }
        
        serializer = ChangePhoneVerifySerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
        
        self.assertFalse(serializer.is_valid())
        self.assertIn('otp', serializer.errors)
