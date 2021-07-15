from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from authentication.models import User
from authentication.validators import ValidatePathSerializerMixin, ValidateEmailSerializerMixin


class ProfileSerializer(serializers.ModelSerializer):
    # TODO: add user's rating

    class Meta:
        model = User
        fields = ('id', 'email')
        read_only_fields = ('id', 'email')


class UserPasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        fields = ('old_password', 'password')

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise ValidationError("Wrong password.")
        return value

    def save(self):
        password = self.validated_data['password']
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        return user


class UserEmailSerializer(ValidateEmailSerializerMixin, ValidatePathSerializerMixin, serializers.ModelSerializer):
    """Here you can see why we created these validation mixins.
    We use the validation in both serializers,
    so this way we overcome the code duplication
    """
    path = serializers.RegexField(regex=r'[a-zA-Z0-9_\-\/]+', required=True, write_only=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'path')
        read_only_fields = ('id',)

    def update(self, instance, validated_data):
        instance.is_active = False
        return super().update(instance, validated_data)
