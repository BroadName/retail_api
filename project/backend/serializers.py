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


class AddProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    class Meta:
        model = Product
        fields = ['id']


class OrderItemSerializer(serializers.ModelSerializer):
    product = AddProductSerializer(read_only=False)
    class Meta:
        model = OrderItem
        fields = ['order','product', 'quantity', 'shop']


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, source='orderitem_set')
    class Meta:
        model = Order
        fields = ['contact', 'order_items']