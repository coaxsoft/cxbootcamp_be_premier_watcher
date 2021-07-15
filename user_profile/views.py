from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from authentication.tokens import TokenGenerator
from authentication import utils
from authentication.models import User
from user_profile import serializers
from notifications.tasks import send_email


class ProfileViewSet(mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):
    """
    retrieve:
    Get profile info

    Get authenticated user profile info.

    change_email:
    Change user email

    Change user email

    deactivate:
    Deactivate user account

    Deactivate user account, instead of hard deletion of User profile
    and all related objects
    """
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.ProfileSerializer

    def get_object(self):
        return self.request.user

    @swagger_auto_schema(request_body=serializers.UserPasswordChangeSerializer,
                         operation_description="Change user password\n"
                                               "use `oldPassword` and `Password` fields for password update.")
    @action(methods=['POST'], detail=False)
    def change_password(self, *args, **kwargs):
        user = self.get_object()

        serializer = serializers.UserPasswordChangeSerializer(data=self.request.data, context={'request': self.request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        send_email.delay(
            subject='Password was successfully changed',
            template='change_password.html',
            recipients=[user.email],
            context={'user_email': user.email}
        )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(request_body=serializers.UserEmailSerializer)
    @action(methods=['PATCH'], detail=False)
    def change_email(self, *args, **kwargs):
        user = self.get_object()
        serializer = serializers.UserEmailSerializer(
            instance=user,
            data=self.request.data,
            context={'request': self.request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        token = f"{urlsafe_base64_encode(force_bytes(user.email))}.{TokenGenerator.make_token(user)}"
        url = utils.construct_url(serializer.validated_data['path'], token)

        send_email.delay(
            subject='Reset Email',
            template='reset_email.html',
            context={'url': url},
            recipients=[user.email]
        )

        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def deactivate(self, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save()

        send_email.delay(
            subject='Your account is deactivated',
            template='deactivated_account.html',
            recipients=[user.email],
            context={}
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
