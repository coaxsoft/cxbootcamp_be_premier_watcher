from django.db.models import OuterRef, Subquery, Sum

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
