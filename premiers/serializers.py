from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
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
    rating = serializers.SerializerMethodField()

    # But annotated fields should be explicitly set!
    is_future = serializers.BooleanField(read_only=True)

    class Meta:
        model = models.Premier

        # is_future is our annotated in get_queryset method field
        fields = ('id', 'url', 'name', 'description', 'user', 'rating', 'is_future', 'premier_at', 'created_at')
        read_only_fields = ('id', 'url', 'user', 'is_future', 'created_at')

    def get_rating(self, obj: models.Premier) -> float:
        """This is how aggregation works. In this example
        we need to calculate and return the total sum of votes of
        the premier.

        Obviously, we do it using DB aggregation.
        """
        obj_type = ContentType.objects.get_for_model(obj)
        rating = models.Vote.objects.filter(
            content_type=obj_type,
            object_id=obj.id
        ).aggregate(sum=Sum('rating'))['sum']

        return rating
