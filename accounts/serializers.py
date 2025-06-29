from rest_framework import serializers
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from utils import verify_otp_auth_num, verify_otp_change_phone


# region Field

class PhoneNumberField(serializers.CharField):
    default_validators = [
        RegexValidator(
            regex=r'^\+98[0-9]{10}$',
            message="Phone number must be entered in the format: '+9891234567890'. Exactly 12 digits allowed."
        )
    ]
    
# endregion

# region Auth

class RequestOTPSerializer(serializers.Serializer):
    phone = PhoneNumberField(max_length=13)


class VerifyOTPSerializer(serializers.Serializer):
    phone = PhoneNumberField(max_length=13)
    otp = serializers.IntegerField(required=True)

    def validate_otp(self, value):
        phone = self.initial_data.get('phone')

        if not verify_otp_auth_num(phone, value):
            raise serializers.ValidationError("Invalid OTP provided. Please try again.")
        return value

# endregion

# region Update

class ChangePhoneRequestSerializer(RequestOTPSerializer):
    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError(
                _("This phone number is already in use. Please use a different number.")
            )
        return value
          
        
class ChangePhoneVerifySerializer(VerifyOTPSerializer):
    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError(
                _("This phone number is already in use. Please use a different number.")
            )
        return value
    
    def validate_otp(self, value):
        phone = self.initial_data.get('phone')
        
        if not verify_otp_change_phone(phone, value):
            raise serializers.ValidationError(
                _("Invalid OTP provided for phone change. Please try again.")
            )
        return value

# endregion