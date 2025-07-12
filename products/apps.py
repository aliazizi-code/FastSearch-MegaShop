from django.apps import AppConfig
import random
import time


class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'products'

    def ready(self):
        import products.signals

        try:
            from products.documents import ProductDocument

            for i in range(5):
                offset = random.randint(0, 100)
                ProductDocument.search() \
                    .query("match_all") \
                    .source(['id', 'title', 'price', 'description']) \
                    [offset:offset + 20] \
                    .execute()

                time.sleep(0.2)

        except Exception as e:
            pass
