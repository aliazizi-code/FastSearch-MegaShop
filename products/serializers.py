from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from .documents import ProductDocument
from .models import Product


class ProductDocumentSerializer(DocumentSerializer):
    class Meta:
        document = ProductDocument
        fields = (
            'title',
            'id',
        )