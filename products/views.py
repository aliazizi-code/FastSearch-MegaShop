from rest_framework import status, response
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    CompoundSearchFilterBackend,
    DefaultOrderingFilterBackend,
)
from django_elasticsearch_dsl_drf.pagination import PageNumberPagination

from .documents import ProductDocument
from .serializers import ProductDocumentSerializer


class ProductDocumentView(DocumentViewSet):
    document = ProductDocument
    serializer_class = ProductDocumentSerializer
    pagination_class = PageNumberPagination
    filter_backends = [
        FilteringFilterBackend,
        CompoundSearchFilterBackend,
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
    
    def list(self, request, *args, **kwargs):
        if not request.GET.get('search'):
            return response.Response(
                {"detail": 'Please provide a search query.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().list(request, *args, **kwargs)
