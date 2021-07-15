from rest_framework.exceptions import ValidationError

from authentication.models import User


class ValidateEmailSerializerMixin:
    """This mixin should be integrated in the serializers
    where we have email field and we need to validate it.

    Include it in inheritance to SignUpSerializer and
    ProfileSerializer (needed when user changes email address)
    """
    def validate_email(self, value):
        """Convert email to lower case and check if email already exists"""
        value = value.lower()
        if User.objects.filter(email=value).exists():
            raise ValidationError('User with this email address already exists.')
        return value


class ValidatePathSerializerMixin:
    """Mixin that includes path field and it's validation

    Use this Mixin in all serializers where FE should send you path, i. e.
    `/activate/user`.

    **NOTE** you must include `path` into you serializer's Meta.fields collection
    and process this field accordingly as ordinary field.
    """

    def validate_path(self, path):
        return path.strip('/')

