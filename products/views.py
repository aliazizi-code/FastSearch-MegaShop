from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from django_elasticsearch_dsl_drf.filter_backends import CompoundSearchFilterBackend
from rest_framework.pagination import CursorPagination
from rest_framework.exceptions import ValidationError

from .documents import ProductDocument
from .serializers import ProductDocumentSerializer
from .filters import FuzzySearchFilterBackend


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
    # pagination_class = ProductListPagination
    filter_backends = [
        FuzzySearchFilterBackend
    ]

    search_fields = (
        'title_fa',
        'title_fa_ngram',
        'title_en',
        'description_fa',
        'description_fa_ngram',
        'description_en',
        'tags_fa',
        'tags_fa_ngram',
        'tags_en',
    )
    
    def get_queryset(self):
        query = self.request.query_params.get('search')
        if not query:
            raise ValidationError("Search query parameter 'search' is required.")
        
        queryset = super().get_queryset()
        return queryset.source(['id', 'title'])