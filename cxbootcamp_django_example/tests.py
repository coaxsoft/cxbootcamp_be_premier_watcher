from django.conf import settings
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import AccessToken

from authentication.models import User


class BaseAPITest(APITestCase):
    """BaseAPITest class contains useful methods to
    automatically create and authorize users via API with JWT
    """
    def create(self, email='test@mail.com', password='test_password'):  # nosec
        user = User.objects.create_user(email=email, password=password)
        user.last_login = timezone.now()
        user.is_active = True
        user.save()

        return user

    def create_and_login(self, email='test@mail.com', password='test_password'):  # nosec
        user = self.create(email=email, password=password)
        self.authorize(user)
        return user

    def authorize(self, user, **additional_headers):
        token = AccessToken.for_user(user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"{api_settings.AUTH_HEADER_TYPES[0]} {token}",
            **additional_headers
        )

    def logout(self, **additional_headers):
        self.client.credentials(**additional_headers)
