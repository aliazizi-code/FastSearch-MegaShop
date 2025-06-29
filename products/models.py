from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager
from utils import AutoSlugField


class ProductManager(models.Manager):
    def published(self):
        return self.filter(is_published=True, is_deleted=False)

    def deleted(self):
        return self.filter(is_deleted=True)


class Product(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('Title'))

    slug = AutoSlugField(
        source_field='title',
        verbose_name=_('Slug'),
        db_index=False
    )

    description = models.TextField(
        verbose_name=_('Description'),
        blank=True,
        null=True
    )
    tags = TaggableManager(verbose_name=_('Tags'), help_text=_('Tags for the product'))

    cached_tags = models.TextField(
        blank=True,
        null=True,
        editable=False,
        help_text=_('Cached tags as plain text for FTS')
    )

    sv = SearchVectorField(
        editable=False,
        null=True,
        help_text=_('Search vector field for full-text search')
    )

    is_published = models.BooleanField(default=False, verbose_name=_('Is Published'))
    is_deleted = models.BooleanField(default=False, verbose_name=_('Is Deleted'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    
    objects = ProductManager()

    class Meta:
        ordering = ['-created_at', 'id']
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        unique_together = [('title', 'slug')]

        indexes = [
            GinIndex(fields=['sv'], name='product_sv_idx'),
            models.Index(
                fields=['is_published'],
                name='published_products_idx',
                condition=models.Q(is_published=True)
            ),
            models.Index(
                fields=['is_deleted'],
                name='deleted_products_idx',
                condition=models.Q(is_deleted=False)
            ),
            models.Index(fields=['slug'], name='product_slug_btree_idx'),
            models.Index(fields=['title'], name='product_title_idx'),
        ]

    def __str__(self):
        return self.title

    def update_cached_tags(self):
        self.cached_tags = ' '.join(self.tags.names())

    def update_search_vector(self):
        from django.contrib.postgres.search import SearchVector
        Product.objects.filter(pk=self.pk).update(
            sv=(
                SearchVector('title', weight='A') +
                SearchVector('cached_tags', weight='B')
            )
        )
