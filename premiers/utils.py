from django.db.models import OuterRef, Subquery, Sum
from elasticsearch_dsl import Q, SF
from elasticsearch_dsl.query import MultiMatch

from premiers.documents import ItemDocument
from premiers.models import Premier, Comment


def subquery_example():
    """An example of how to use Subquery in Django ORM.

    Real world example are much harder
    """
    subquery = Comment.objects.annotate(
        rating=Sum('votes__rating')
    ).filter(premier_id=OuterRef("id")).order_by('-rating').values('id')[:1]
    qs = Premier.objects.filter(is_active=True).annotate(
        top_comment_id=Subquery(subquery)
    )
    return qs


def get_search_query(phrase):
    query = {
        "bool": {
            "must": [
                {
                    "multi_match": {
                        "query": phrase,
                        "fields": ["name", "description"],
                        "analyzer": "standard"
                    }
                }
            ],
        }
    }
    return ItemDocument.search().query(query)


def search(phrase):
    offset = 0
    limit = 500
    return get_search_query(phrase)[offset:limit].to_queryset()
