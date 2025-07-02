from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from .documents import ProductDocument


class ProductDocumentSerializer(DocumentSerializer):
    class Meta:
        document = ProductDocument
        fields = (
            'id',
            'title',
            'description',
            'is_published',
            'is_deleted',
            'cached_tags',
        )
