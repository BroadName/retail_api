from django.contrib import admin
from .models import Shop, Order, OrderItem, Product, ProductInfo, ProductParameter, Parameter, Category


admin.site.register(Shop)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Parameter)
admin.site.register(Product)
admin.site.register(ProductInfo)
admin.site.register(ProductParameter)
admin.site.register(Category)