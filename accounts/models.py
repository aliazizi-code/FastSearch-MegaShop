from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from utils import PhoneNumberField
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    phone = PhoneNumberField(verbose_name=_("Phone Number"))
    first_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('First Name')
    )
    last_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('Last Name')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is Active')
    )
    is_admin = models.BooleanField(
        default=False,
        verbose_name=_('Is Admin')
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name=_('Is Staff')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at')
    )

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['created_at']
        db_table = 'custom_user'
        indexes = [
            models.Index(fields=['phone']),
        ]

    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name.capitalize()} {self.last_name.capitalize()}"
        return None

    def __str__(self):
        full_name = self.full_name()
        return f"{full_name} ({self.phone})" if full_name else self.phone
