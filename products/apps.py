from django.apps import AppConfig
from django_elasticsearch_dsl import Index


class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'products'
    
    def ready(self):
        import products.signals
        
        # Warm up the ES cache by running a lightweight match_all query
        try:
            idx = Index('products')
            idx.search().query("match_all")[0:1].execute()
        except Exception:
            pass
