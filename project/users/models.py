from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from .managers import CustomUserManager


USER_TYPE_CHOICES = (
    ('buyer', 'Покупатель'),
    ('shop', 'Магазин'),
)


class BaseUser(AbstractUser):

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'

    objects = CustomUserManager()

    username = None
    email = models.EmailField(_('email_address'), unique=True)
    type = models.CharField(verbose_name='Тип пользователя', choices=USER_TYPE_CHOICES, max_length=5, default='buyer')
    is_active = models.BooleanField(
        _('active'),
        default=False,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.email


class CustomUser(BaseUser):

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Список пользователей'
        ordering = ('email',)
