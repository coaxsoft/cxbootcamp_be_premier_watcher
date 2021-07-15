from rest_framework import serializers

from authentication.models import User
from premiers import models


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'email')
        read_only_fields = fields


class PremierSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = models.Premier
        fields = ('id', 'url', 'name', 'description', 'user', 'premier_at', 'created_at')
        read_only_fields = ('id', 'url', 'user', 'created_at')
