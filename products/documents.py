from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl.registries import registry
from .models import Product


product_index = Index('products')

product_index.settings(
    number_of_shards=1,
    number_of_replicas=0,
    analysis={
        "analyzer": {
            "rebuilt_persian": {
                'tokenizer': "standard",
                "filter": [
                    "lowercase",
                    'arabic_normalization',
                    'persian_normalization',
                ]
            }
        }
    }
)


@registry.register_document
class ProductDocument(Document):
    cached_tags = fields.TextField(analyzer="rebuilt_persian")
    title = fields.TextField(analyzer="rebuilt_persian")
    description = fields.TextField(analyzer="rebuilt_persian")
    
    class Index:
        name = 'products'
        settings = product_index._settings
        
    class Django:
        model = Product
        fields = ['is_published', 'is_deleted']
        
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True, is_deleted=False)
