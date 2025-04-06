from django.urls import path
from .views import (
    RegistrationView,
    UserLoginView,
    UserLogoutView
)

urlpatterns = [
    path("registration/", RegistrationView.as_view(), name="registration"),
    path("userlogin/", UserLoginView.as_view(), name="login"),
    path("userlogout", UserLogoutView.as_view(), name="logout"),
]
