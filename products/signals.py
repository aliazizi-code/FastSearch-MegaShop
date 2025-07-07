from django.db.models.signals import post_save, m2m_changed, post_delete
from django.dispatch import receiver
from .models import Product
from .documents import ProductDocument


@receiver(m2m_changed, sender=Product.tags.through)
def schedule_tag_vector_update(sender, instance, action, **kwargs):
    if action in ['post_add', 'post_remove', 'post_clear']:
        instance.cached_tags = ','.join(instance.tags.names())
        
        Product.objects.filter(pk=instance.pk).update(cached_tags=instance.cached_tags)


@receiver(post_save, sender=Product)
def index_product_if_valid(sender, instance, **kwargs):
    doc = ProductDocument()
    if instance.is_published and not instance.is_deleted:
        doc.update(instance)
    else:
        doc.delete(instance)

@receiver(post_delete, sender=Product)
def remove_product_from_index(sender, instance, **kwargs):
    ProductDocument().delete(instance)