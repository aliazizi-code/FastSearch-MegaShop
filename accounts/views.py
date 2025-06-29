# Django Imports
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.middleware.csrf import rotate_token, get_token

# Third Party Imports
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.serializers import TokenBlacklistSerializer
from rest_framework_simplejwt.tokens import RefreshToken, Token
from rest_framework_simplejwt.views import TokenRefreshView

# Local Application Imports
from accounts.models import User
from accounts.serializers import *
from accounts.throttles import DualThrottle
from accounts.permissions import IsAnonymous
from accounts.jwt import set_token_cookies, delete_token_cookies
from accounts.tasks import send_otp_to_phone_tasks
from utils import generate_otp_change_phone, generate_otp_auth_num


class RefreshTokenAPIView(TokenRefreshView):
    def post(self, request: Request, *args, **kwargs) -> Response:
        try:
            serializer = self.get_serializer(data={"refresh": self.get_refresh_token_from_cookie()})
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0]) from e

        response = Response({
            "success": True,
            "message": "Tokens have been successfully refreshed."},
            status=status.HTTP_200_OK)

        # Set auth cookies
        access_token = serializer.validated_data.get("access")
        refresh_token = serializer.validated_data.get("refresh")
        set_token_cookies(response, access_token, refresh_token)

        return response

    def get_refresh_token_from_cookie(self) -> Token:
        refresh = self.request.COOKIES.get("refresh_token")
        if not refresh:
            raise PermissionDenied

        return refresh
    

class CSRFAPIView(APIView):
    permission_classes = ()
    authentication_classes = ()

    def get(self, request):
        return Response({"token": get_token(request)})


# region Auth

class BaseLoginView(APIView):
    serializer_class = None

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            user = serializer.validated_data['user']
            return Response(data=self._handle_login(user, request), status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _handle_login(self, user, request, created=False):
        response = Response(status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

        # Set auth cookies
        refresh = RefreshToken.for_user(user)
        set_token_cookies(response, str(refresh.access_token), str(refresh))

        # Rotate CSRF token
        # Django: For security reasons, CSRF tokens are rotated each time a user logs in.
        rotate_token(request)

        return response


class RequestOTPView(APIView):
    serializer_class = RequestOTPSerializer
    permission_classes = [IsAnonymous]
    throttle_classes = [DualThrottle]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            phone = data['phone']
            created = User.objects.filter(phone=phone).exists()

            otp = generate_otp_auth_num(phone)
            send_otp_to_phone_tasks.delay(otp)
            
            data = {'created': not created,}
            
            if settings.DEBUG:
                data['otp'] = otp

            return Response(
                data=data,
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTPView(BaseLoginView):
    serializer_class = VerifyOTPSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            user, created = User.objects.get_or_create(phone=data['phone'])

            user.last_login = timezone.now()
            user.save()

            return self._generate_response(user, created, request)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _generate_response(self, user, created, request):
        response = self._handle_login(user, request, created)

        response.data = {
            'message': 'User verified successfully',
            'created': created,
            'phone': str(user.phone)
        }

        return response


class LogoutAPIView(APIView):
    serializer_class = TokenBlacklistSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data={"refresh": self.get_refresh_token_from_cookie(request)})

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0]) from e

        response = Response({}, status=status.HTTP_200_OK)

        # Delete jwt cookies
        delete_token_cookies(response)

        return response

    def get_refresh_token_from_cookie(self, request) -> Token:
        refresh = self.request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"])
        if not refresh:
            raise PermissionDenied

        return refresh

# endregion

# region Update

class ChangePhoneRequestView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePhoneRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            
            otp = generate_otp_change_phone(data['phone'])
            send_otp_to_phone_tasks.delay(otp)
            
            data = {}
            
            if settings.DEBUG:
                data['otp'] = otp
                    
            return Response(data=data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePhoneVerifyView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePhoneVerifySerializer

    def post(self, request):
        user = request.user
        serializer = self.serializer_class(data=request.data, context={'request': request})

        if serializer.is_valid():
            data = serializer.validated_data
            
            user.phone = data["phone"]
            user.save()
            return Response(
                {"detail": _("Your phone number has been changed successfully.")},
                status=status.HTTP_200_OK)
             
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# endregion
