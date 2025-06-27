from django.urls import path
from accounts import views

urlpatterns = [
    # Auth
    path("auth/refresh_token/", views.RefreshTokenAPIView.as_view(), name="refresh-token"),
]
