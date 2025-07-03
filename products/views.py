from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from django_elasticsearch_dsl_drf.filter_backends import CompoundSearchFilterBackend
from rest_framework.pagination import CursorPagination
from rest_framework.exceptions import ValidationError

from .documents import ProductDocument
from .serializers import ProductDocumentSerializer


class ProductListPagination(CursorPagination):
    page_size = 16
    page_size_query_param = 'page_size'
    max_page_size = 48
    
    def get_ordering(self, request, queryset, view):
        if queryset.query.order_by:
            return queryset.query.order_by
        return super().get_ordering(request, queryset, view)


class ProductDocumentView(DocumentViewSet):
    document = ProductDocument
    serializer_class = ProductDocumentSerializer
    pagination_class = ProductListPagination
    filter_backends = [CompoundSearchFilterBackend]

    search_fields = (
        'title.fa',
        'title.en',
        'description.fa',
        'description.en',
        'tags.fa',
        'tags.en',
    )
    
    def get_queryset(self):
        query = self.request.query_params.get('search')
        if not query:
            raise ValidationError("Search query parameter 'search' is required.")
        return super().get_queryset()