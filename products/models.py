from django.db import models
from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager


class ProductManager(models.Manager):
    def published(self):
        return self.filter(is_published=True, is_deleted=False)

    def deleted(self):
        return self.filter(is_deleted=True)


class Product(models.Model):
    title = models.CharField(max_length=200, verbose_name=_('Title'))

    description = models.TextField(
        verbose_name=_('Description'),
        blank=True,
        null=True
    )
    tags = TaggableManager(
        verbose_name=_('Tags'),
        help_text=_('Tags for the product'),
        blank=True
    )

    cached_tags = models.TextField(
        blank=True,
        null=True,
        editable=False,
        help_text=_('Cached tags as plain text for FTS')
    )

    is_published = models.BooleanField(default=False, verbose_name=_('Is Published'))
    is_deleted = models.BooleanField(default=False, verbose_name=_('Is Deleted'))

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    
    objects = ProductManager()

    def __str__(self):
        return self.title
