from django.db import models
from django.conf import settings

from users.models import Contact

STATUS_CHOICES = (
    ('basket', 'Статус корзины'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)


class Shop(models.Model):
    name = models.CharField(max_length=80, verbose_name='Название')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             verbose_name='Пользователь',
                             blank=True, null=True)
    url = models.URLField(max_length=255, null=True, blank=True, verbose_name='Ссылка')

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Список магазинов'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Category(models.Model):
    shops = models.ManyToManyField(Shop, verbose_name='Магазины', related_name='categories', blank=True)
    external_id = models.PositiveIntegerField(verbose_name='Внешний ID')
    name = models.CharField(max_length=50, verbose_name='Название')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Список категорий'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Категория')
    name = models.CharField(max_length=80, verbose_name='Название')

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Список продуктов'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    model = models.CharField(max_length=80, verbose_name='Модель', blank=True)
    external_id = models.PositiveIntegerField(verbose_name='Внешний ID')
    product = models.ForeignKey(Product,
                                on_delete=models.CASCADE, verbose_name='Продукт',
                                related_name='product_info',
                                blank=True)
    shop = models.ForeignKey(Shop,
                             on_delete=models.CASCADE,
                             verbose_name='Магазин',
                             related_name='product_info',
                             blank=True)
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.PositiveIntegerField(verbose_name='Цена')
    price_rrc = models.PositiveIntegerField(verbose_name='Розничная цена')

    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = 'Информация о продуктах'
        ordering = ('-model',)


    def __str__(self):
        return f'{self.product} : {self.quantity} pieces'

class Parameter(models.Model):
    name = models.CharField(max_length=80, verbose_name='Название')

    class Meta:
        verbose_name = 'Имя параметра'
        verbose_name_plural = 'Список имён параметров'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    product_info = models.ForeignKey(ProductInfo,
                                     on_delete=models.CASCADE,
                                     verbose_name='Информация о продукте',
                                     related_name='product_parameters',
                                     blank=True)
    parameter = models.ForeignKey(Parameter,
                                  on_delete=models.CASCADE,
                                  verbose_name='Параметр',
                                  related_name='product_parameters',
                                  blank=True)
    value = models.CharField(max_length=150, verbose_name='Значение')

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = 'Список параметров'
        constraints = [
            models.UniqueConstraint(fields=['product_info', 'parameter'], name='unique_product_parameter'),
        ]

    def __str__(self):
        return f'{self.product_info.model} - {self.parameter.name} : {self.value}'

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             verbose_name='Пользователь',
                             related_name='orders')
    dt = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    status = models.CharField(max_length=12, default='new', verbose_name='Статус', choices=STATUS_CHOICES)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, verbose_name='Контактная информация', blank=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Список заказов'
        ordering = ('-dt',)

    def __str__(self):
        return f'status: {self.status} -> {self.user}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Заказ', blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Продукт', blank=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name='Магазин', blank=True)
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Общая стоимость')

    class Meta:
        verbose_name = 'Заказанная позиция'
        verbose_name_plural = 'Список заказанных позиций'
        ordering = ('-pk',)


    def __str__(self):
        return f'{self.order} | {self.product} * {self.quantity} pieces'

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.product.product_info.first().price_rrc
        super().save(*args, **kwargs)