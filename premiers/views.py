from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from cxbootcamp_django_example.paginators import ResultSetPagination
from premiers.models import Premier
from premiers.serializers import PremierSerializer


class PremierViewSet(mixins.ListModelMixin,
                     mixins.CreateModelMixin,
                     viewsets.GenericViewSet):
    """
    list:
    Get list of premiers

    Get list of premiers

    create:
    Create new premier

    Create new premier
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = PremierSerializer
    queryset = Premier.objects.filter(is_active=True)
    pagination_class = ResultSetPagination

    def perform_create(self, serializer):
        """Overriding perform_create method is an elegant solution on
        sharing dynamic data from view to serializer. Here to
        save Premier, we share authenticated user to attach to Premier
        and we don't need to write ``create(...)`` method for PremierSerializer
        """
        serializer.save(user=self.request.user)
