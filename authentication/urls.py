from django.urls import path
from .views import (
    RegistrationView,
    UserLoginView,
)

urlpatterns = [
    path("registration/", RegistrationView.as_view(), name="registration"),
    path("userlogin/", UserLoginView.as_view(), name="login")
]
