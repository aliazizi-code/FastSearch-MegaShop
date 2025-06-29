from django.urls import path
from .views import *

urlpatterns = [
    # Authentication Endpoints
    path("auth/otp/request/", RequestOTPView.as_view(), name="request-otp"),
    path("auth/otp/verify/", VerifyOTPView.as_view(), name="verify-otp"),
    path("auth/token/refresh/", RefreshTokenAPIView.as_view(), name="token-refresh"),
    path("auth/logout/", LogoutAPIView.as_view(), name="logout"),
    
    # Phone Number Management
    path("user/phone/change/request/", ChangePhoneRequestView.as_view(), name="change-phone-request"),
    path("user/phone/change/verify/", ChangePhoneVerifyView.as_view(), name="change-phone-verify"),
    
    # CSRF
    path("csrf_token/", CSRFAPIView.as_view(), name="csrf-token"),
]
