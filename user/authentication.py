from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from user.models import CustomToken

class CustomTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token_key = request.headers.get('Authorization')
        if not token_key:
            return None
        token_key = token_key.split("Token ")[-1]
        try:
            token = CustomToken.objects.get(key=token_key)
        except CustomToken.DoesNotExist:
            raise AuthenticationFailed('Invalid token')
        return (token.user, token)
