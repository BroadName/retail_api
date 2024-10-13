import uuid

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


class Contact(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='contacts',
                             verbose_name='Пользователь')
    city = models.CharField(max_length=50, verbose_name='Город')
    street = models.CharField(max_length=100, verbose_name='Улица')
    house = models.CharField(max_length=20, verbose_name='Дом', blank=True)
    structure = models.CharField(max_length=20, verbose_name='Корпус', blank=True)
    building = models.CharField(max_length=20, verbose_name='Строение', blank=True)
    apartment = models.CharField(max_length=20, verbose_name='Квартира', blank=True)
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    additional_desc = models.TextField(verbose_name='Дополнительная информация', blank=True, null=True)

    class Meta:
        verbose_name = 'Контактная информация'
        verbose_name_plural = 'Список контактной информации'
        ordering = ('-city',)

    def __str__(self):
        return f'{self.city}, {self.street}, {self.house}'


class ConfirmToken(models.Model):
    token = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tokens')
    dt = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Токен подтверждения'
        verbose_name_plural = 'Список токенов подтверждения'