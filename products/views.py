from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    SearchFilterBackend,
    DefaultOrderingFilterBackend,
)
from django_elasticsearch_dsl_drf.pagination import PageNumberPagination

from .documents import ProductDocument
from .models import Product


class ProductDocumentView(DocumentViewSet):
    document = ProductDocument
    pagination_class = PageNumberPagination
    filter_backends = [
        FilteringFilterBackend,
        SearchFilterBackend,
        DefaultOrderingFilterBackend,
    ]

    search_fields = (
        'title',
        'description',
        'cached_tags',
    )

    filter_fields = {
        'is_published': 'is_published',
        'is_deleted': 'is_deleted',
    }

    ordering_fields = {
        'title': 'title.keyword',
    }

    ordering = ('title',)
