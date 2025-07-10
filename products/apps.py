from django.apps import AppConfig
import logging
import random
import time

logger = logging.getLogger(__name__)


class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'products'

    def ready(self):
        import products.signals

        try:
            from products.documents import ProductDocument

            for i in range(5):
                logger.debug(f"🔥 Warm-up pass {i+1}/3 ...")

                offset = random.randint(0, 100)
                ProductDocument.search() \
                    .query("match_all") \
                    .source(['id', 'title', 'price', 'description']) \
                    [offset:offset + 20] \
                    .execute()

                time.sleep(0.2)

        except Exception as e:
            logger.warning("❌ Elasticsearch warm-up failed:", exc_info=e)
