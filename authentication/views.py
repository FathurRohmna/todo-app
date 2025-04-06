from django.shortcuts import render
from django.views import View
from django.contrib import messages

# Create your views here.
class RegistrationView(View):
    def get(self, request):
        messages.get_messages(request)
        return render(request, "authentication/register.html")
    
class UserLoginView(View):
    def get(self, request):
        return render(request, "authentication/login.html")
