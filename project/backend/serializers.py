from rest_framework import serializers

from .models import Order, OrderItem, Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Contact


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ['id', 'name']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name']


class ProductInfoSerializer(serializers.ModelSerializer):
    shop = ShopSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    class Meta:
        model = ProductInfo
        fields = ['model', 'quantity', 'price_rrc', 'shop', 'product']