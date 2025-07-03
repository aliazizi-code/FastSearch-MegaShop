from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from .documents import ProductDocument
from .models import Product


class ProductDocumentSerializer(DocumentSerializer):
    class Meta:
        document = ProductDocument
        fields = (
            'title',
            'slug',
        )
    
    def get_slug(self, obj):
        try:
            product = Product.objects.only('slug').get(pk=obj.meta.id)
            return product.slug
        except Product.DoesNotExist:
            return None
