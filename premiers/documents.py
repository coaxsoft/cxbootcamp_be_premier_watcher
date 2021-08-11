from django_elasticsearch_dsl import Index, Document

from premiers.models import Premier


premiers = Index('premiers')
premiers.settings(number_of_shards=1, number_of_replicas=0)


@premiers.doc_type
class ItemDocument(Document):

    class Django:
        model = Premier
        fields = ('name', 'description')
