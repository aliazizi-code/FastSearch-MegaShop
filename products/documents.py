from django_elasticsearch_dsl import Document, Index, fields
from django_elasticsearch_dsl.registries import registry
from .models import Product


product_index = Index('products')

product_index.settings(
    number_of_shards=1,
    number_of_replicas=0,
    analysis={
        "char_filter": {
            "zero_width_spaces": {
                "type": "mapping",
                "mappings": [ "\\u200C=>\\u0020"]
            }
        },
        "filter": {
            "persian_stop": {
            "type": "stop",
            "stopwords":  "_persian_"
            }
        },
        "analyzer": {
            "rebuilt_persian": {
                "tokenizer":     "standard",
                "char_filter": [ "zero_width_spaces" ],
                "filter": [
                    "lowercase",
                    "decimal_digit",
                    "arabic_normalization",
                    "persian_normalization",
                    "persian_stop",
                    "persian_stem"
                ]
            }
        }
    }
)


@registry.register_document
class ProductDocument(Document):
    title = fields.TextField(
        analyzer="rebuilt_persian",
        fields={
            'keyword': fields.KeywordField()
        }
    )
    description = fields.TextField(
        analyzer="rebuilt_persian",
        fields={
            'keyword': fields.KeywordField()
        }
    )
    cached_tags = fields.TextField(analyzer="rebuilt_persian")
    
    class Index:
        name = 'products'
        settings = product_index._settings
        
    class Django:
        model = Product
        fields = ['is_published', 'is_deleted']
        
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True, is_deleted=False)
