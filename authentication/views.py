from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from drf_yasg.utils import swagger_auto_schema

from rest_framework.generics import CreateAPIView, get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenVerifySerializer, \
    TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenVerifyView, TokenRefreshView

from authentication import utils
from authentication import serializers
from authentication.models import User
from authentication.schema import JSONTokenSchema
from authentication.tokens import TokenGenerator
from cxbootcamp_django_example.schema import NO_CONTENT
from notifications.tasks import send_email


class ObtainJSONWebToken(TokenObtainPairView):
    """
    post:
    Generate REST API token.

    Generate personal REST API token with expired date `ACCESS_TOKEN_LIFETIME_HOURS` or/and
    `ACCESS_TOKEN_LIFETIME_MINUTES` (1 day).

    In a few words - it's an authentication token. To work with API you need to have it, entering your email
    and password. Each time you request to the API, you need to send in header your token like
    `Authorization: JWT eyJ0eXAiOiJKV...`, where `JWT` is header authorization prefix.

    ### Examples

    If data is successfully processed the server returns status code `200`.

    ```json
    {
        "email": "email@coaxsoft.com",
        "password": "qwerty123"
    }
    ```

    ### Errors

    If there were some error in client data, it sends status code `401`.
    """
    serializer_class = TokenObtainPairSerializer


class VerifyJSONWebToken(TokenVerifyView):
    """
    post:
    Verify your token (is it valid?)

    To work with API you need to have valid (verified) token which you get after visiting `/auth/token-verify`
    url, entering your token.[Read JWT docs](https://jwt.io/)

    ### Examples

    If data is successfully processed the server returns status code `200`.

    ```json
    {
        "token": "emskdlgnkngdDFHGergergEGRerRGEgerERE346346vergd456456"
    }
    ```

    ### Errors

    If there were some error in client data, it sends status code `401` with the error message looks like:

    ```json
    {
        "detail": "Token is invalid or expired",
        "code": "token_not_valid"
    }
    ```
    """
    serializer_class = TokenVerifySerializer


class RefreshJSONWebToken(TokenRefreshView):
    """
    post:
    Refresh expired JSON Web Token.

    It is used JWT authentication with refresh expiration time = 14 days [Read JWT docs](https://jwt.io/). It
    means, that you have 14 days, from the time your token was generated, to update token with new one. So
    that you need to send your JSON WEB Token.

    ### Examples

    If data is successfully processed the server returns status code `200`.

    ```json
    {
        "refresh": "emskdlgnkngdDFHGergergEGRerRGEgerERE346346vergd456456"
    }
    ```

    ### Errors

    If there were some error in client data, it sends status code `401` with the error message looks like:

    ```json
    {
        "detail": "Token is invalid or expired",
        "code": "token_not_valid"
    }
    ```
    """
    serializer_class = TokenRefreshSerializer


class SignUpView(CreateAPIView):
    """
    Register new user in the system

    You need to provide `email`, `username`, `password`. All the other information
    is additional
    """
    serializer_class = serializers.SignUpSerializer

    def perform_create(self, serializer):
        super().perform_create(serializer)
        user = serializer.instance
        token = f"{urlsafe_base64_encode(force_bytes(user.email))}.{TokenGenerator.make_token(user)}"

        send_email.delay(
            subject="Welcome to Premiers",
            template="activation.html",
            recipients=[user.email],
            context={
                'url': utils.construct_url(serializer.validated_data['path'], token),
            }
        )


class ActivateUserView(APIView):
    """Activate user account

    Activate user account. You must provide
    `token` that was sent to FE as query parameter.
    """
    serializer_class = serializers.ActivationTokenSerializer

    @swagger_auto_schema(
        request_body=serializers.ActivationTokenSerializer,
        responses={
            '200': JSONTokenSchema
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.activate_user()
        user = get_object_or_404(User, email=serializer.validated_data['email'])
        token = RefreshToken.for_user(user)
        return Response(data={'access': str(token.access_token),
                              'refresh': str(token)})


class ResetPasswordView(APIView):
    """Reset user's password

    Need to send email and path to FE.
    ``path`` field is path to FE reset password page
    """
    serializer_class = serializers.ResetPasswordSerializer

    @swagger_auto_schema(
        request_body=serializers.ResetPasswordSerializer,
        responses={204: NO_CONTENT}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self._send_email(serializer.validated_data['email'], serializer.validated_data['path'])
        user = User.objects.get(email=serializer.validated_data['email'])
        user.is_restoring_password = True
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _send_email(email, path):
        user = User.objects.get(email=email)
        token = f"{urlsafe_base64_encode(force_bytes(user.email))}.{TokenGenerator.make_token(user)}"
        url = utils.construct_url(path, token)

        send_email.delay(
            subject='Reset Password',
            template='reset_password.html',
            context={'url': url},
            recipients=[user.email]
        )


class RestorePasswordView(APIView):
    """Restore user's password

    Restore user's password with given token and new password
    """
    serializer_class = serializers.RestorePasswordSerializer

    @swagger_auto_schema(
        request_body=serializers.RestorePasswordSerializer,
        responses={204: NO_CONTENT}
    )
    def post(self, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email=serializer.validated_data['email'])
        user.set_password(serializer.validated_data['password'])
        user.is_restoring_password = False
        user.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
