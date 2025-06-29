from celery import shared_task
from django.db import transaction
import logging
from .models import Product

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def update_product_search_vector(self, product_id):
    try:
        product = Product.objects.get(id=product_id)

        old_cached_tags = product.cached_tags

        with transaction.atomic():
            product.update_cached_tags()

            if product.cached_tags != old_cached_tags:
                product.save(update_fields=['cached_tags'])

            product.update_search_vector()

    except Product.DoesNotExist:
        logger.warning(f"Product with ID {product_id} does not exist.")
        return

    except Exception as e:
        logger.error(f"Error updating product search vector: {e}")
        raise self.retry(exc=e)
