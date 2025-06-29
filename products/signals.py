from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import Product
from .tasks import update_product_search_vector


@receiver(post_save, sender=Product)
def schedule_search_vector_update(sender, instance, **kwargs):
    update_product_search_vector.delay(instance.id)

@receiver(m2m_changed, sender=Product.tags.through)
def schedule_tag_vector_update(sender, instance, action, **kwargs):
    if action in ['post_add', 'post_remove', 'post_clear']:
        update_product_search_vector.delay(instance.id)
