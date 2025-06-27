from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from utils import PhoneNumberField
from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    phone = PhoneNumberField(verbose_name=_("Phone Number"))
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

    def __str__(self):
        return f"{self.phone}"
