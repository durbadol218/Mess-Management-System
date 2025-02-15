# backends.py
from django.contrib.auth.backends import ModelBackend
from user.models import User_Model

class CustomAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User_Model.objects.get(username=username)
            if user.check_password(password):
                return user
        except User_Model.DoesNotExist:
            return None
