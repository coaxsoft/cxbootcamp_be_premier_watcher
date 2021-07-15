from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from authentication.models import User
from authentication.tokens import TokenGenerator
from authentication.validators import ValidatePathSerializerMixin, ValidateEmailSerializerMixin


class SignUpSerializer(ValidatePathSerializerMixin, ValidateEmailSerializerMixin, serializers.ModelSerializer):
    """Create new user when sign up.

    Note! Password should always be write only!

    You may be interested what is the ``path`` field.
    Usually, we use it when we need to send an email to user
    and we include this path/ to FE endpoint to handle
    further user's activation.
    """
    password = serializers.CharField(write_only=True)
    path = serializers.RegexField(regex=r'[a-zA-Z0-9_\-\/]+', required=True, write_only=True)

    class Meta:
        model = User
        fields = ("id", "email", "password", "path",)
        read_only_fields = ("id",)
        write_only_fields = ("password", "path",)

    def create(self, validated_data):
        exclude = {'path', 'captcha'}
        vd = {k: v for k, v in validated_data.items() if k not in exclude}
        return User.objects.create_user(**vd)


class ActivationTokenSerializer(serializers.Serializer):
    """Serializer to accept and validate token sent to user's email"""
    token = serializers.CharField()

    def validate(self, data):
        token = data['token']
        error = f"Provided activation token '{token}' is not valid"
        try:
            uid, token = token.split('.')
            uid = force_text(urlsafe_base64_decode(uid))
        except (TypeError, ValueError):
            raise ValidationError(error)
        try:
            user = User.objects.get(email=uid)
        except User.DoesNotExist:
            raise ValidationError(error)

        if not TokenGenerator.check_token(user, token):
            raise ValidationError(error)

        data['email'] = uid
        return data

    def activate_user(self):
        user = User.objects.get(email=self.validated_data['email'])
        user.is_active = True
        user.save()


class ResetPasswordSerializer(ValidatePathSerializerMixin, serializers.Serializer):
    """Serializer to reset user's password. Used in forget password endpoint"""
    email = serializers.EmailField(required=True)
    path = serializers.RegexField(regex=r'[a-zA-Z0-9_\-\/]+', required=True, write_only=True)

    def validate(self, data):
        if not User.objects.filter(email=data['email']).exists():
            raise ValidationError("User with this email doesn't exist")
        return data


class RestorePasswordSerializer(serializers.Serializer):
    """Serializer to restore password.
    Used when user send a token from email and new password
    """
    password = serializers.CharField(required=True)
    token = serializers.CharField(required=True)

    def validate(self, data):
        try:
            email_b64, token = data['token'].split('.')
            data['email'] = urlsafe_base64_decode(email_b64).decode('utf-8')
            user = User.objects.get(email=data['email'])
        except ValueError:
            raise ValidationError("Email is not valid base64 string.")
        except User.DoesNotExist:
            raise ValidationError("User with this email doesn't exist.")
        if not user.is_restoring_password:
            raise ValidationError("Password reset link has been expired.")
        if not TokenGenerator.check_token(user, token):
            raise ValidationError("Token is invalid or expired.")
        return data
