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
            },
            "edge_ngram_filter": {
                "type": "edge_ngram",
                "min_gram": 2,
                "max_gram": 20
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
            },
            "rebuilt_persian_ngram": {
                "tokenizer":   "standard",
                "char_filter": ["zero_width_spaces"],
                "filter": [
                    "lowercase",
                    "decimal_digit",
                    "arabic_normalization",
                    "persian_normalization",
                    "persian_stop",
                    "persian_stem",
                    "edge_ngram_filter"
                ]
            }
        }
    }
)


@registry.register_document
class ProductDocument(Document):
    title_fa = fields.TextField(
    attr="title",
    analyzer="rebuilt_persian",
    search_analyzer="rebuilt_persian"
    )
    title_fa_ngram = fields.TextField(
        attr="title",
        analyzer="rebuilt_persian_ngram",
        search_analyzer="rebuilt_persian"
    )
    title_en = fields.TextField(attr="title")
    
    description_fa = fields.TextField(
    attr="description",
    analyzer="rebuilt_persian",
    search_analyzer="rebuilt_persian"
    )
    description_fa_ngram = fields.TextField(
        attr="description",
        analyzer="rebuilt_persian_ngram",
        search_analyzer="rebuilt_persian"
    )
    description_en = fields.TextField(attr="description")
    
    tags_fa = fields.TextField(
    attr="cached_tags",
    analyzer="rebuilt_persian",
    search_analyzer="rebuilt_persian"
    )
    tags_fa_ngram = fields.TextField(
        attr="cached_tags",
        analyzer="rebuilt_persian_ngram",
        search_analyzer="rebuilt_persian"
    )
    tags_en = fields.TextField(attr="cached_tags")

    
    class Index:
        name = 'products'
        settings = product_index._settings
        
    class Django:
        model = Product
        fields = ['title', 'id']
        
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True, is_deleted=False)
    
    def should_index_instance(self, instance):
        return instance.is_published and not instance.is_deleted

