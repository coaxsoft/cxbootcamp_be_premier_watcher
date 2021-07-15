from django.core.files.storage import default_storage
from django.db.models.fields.files import FieldFile
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.fields import SkipField
from rest_framework.relations import PKOnlyObject


class ModelFileSerializer(serializers.ModelSerializer):
    """Parent serializer for ones that have models with File fields.
    This overrides default behaviour and fix bug when serialization is
    broken when file is absent
    """
    def to_representation(self, instance):
        ret = {}
        fields = self._readable_fields

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            check_for_none = attribute.pk if isinstance(attribute, PKOnlyObject) else attribute

            # Here we check not for is None but just
            # for ``not check_for_none`` allowing Python + that Django
            # ImageFieldFile to resolve the condition
            if isinstance(attribute, FieldFile) and not check_for_none:
                ret[field.field_name] = None
            elif check_for_none is None:
                ret[field.field_name] = None
            else:
                ret[field.field_name] = field.to_representation(attribute)

        return ret


class ImageUploadSerializer(serializers.Serializer):
    name = serializers.CharField()
    url = serializers.URLField(read_only=True)

    def validate_name(self, value):
        if not default_storage.exists(value):
            error = f"Media file with the name {value} is not found"
            raise NotFound(error)
        return value
