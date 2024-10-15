from django.core.validators import URLValidator
from django.db.models import Sum
from django.http import JsonResponse
from requests import get
from rest_framework import filters, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView, CreateAPIView, DestroyAPIView, UpdateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from yaml import Loader, load as load_yaml

from .permissions import IsOwnerOrderItem, IsOwnerOrder
from .models import (Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem)
from .serializers import (ProductInfoSerializer, OrderSerializer, ListItemsSerializer, OrderItemSerializer,
                          ListOrderSerializer, ConfirmOrderSerializer, GetOrderSerializer)


class UploadProductsView(APIView):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'Error': 'Log in required.'}, status=403)

        if request.user.type != 'shop':
            return JsonResponse({'Error': 'Only shops can upload products.'}, status=403)

        url = request.data.get('url')
        if url:
            validate = URLValidator()
            try:
                validate(url)
            except ValidationError as er:
                return JsonResponse({'Error': str(er)}, status=400)

            else:
                stream = get(url).content
                data = load_yaml(stream, Loader=Loader)

                try:
                    shop, created = Shop.objects.get_or_create(
                        name=data['shop'],
                        user_id = request.user.id
                        )

                    for category in data.get('categories'):
                        category_obj, created = Category.objects.get_or_create(
                            external_id=category['id'],
                            name=category['name']
                        )
                        category_obj.shops.set([shop.id])

                    for product in data.get('goods'):
                        product_obj, created = Product.objects.get_or_create(
                            name = product['name'],
                            category = Category.objects.get(external_id = product['category'])
                        )

                        product_info_obj, created = ProductInfo.objects.get_or_create(
                            product = product_obj,
                            model = product['model'],
                            external_id = product['id'],
                            shop = shop,
                            quantity = product['quantity'],
                            price = product['price'],
                            price_rrc = product['price_rrc']
                        )

                        for key, value in product['parameters'].items():

                            parameter_obj, created = Parameter.objects.get_or_create(
                                name = key
                            )

                            product_parameter_obj, created = ProductParameter.objects.get_or_create(
                                product_info = product_info_obj,
                                parameter = parameter_obj,
                                value = value
                            )

                    return JsonResponse({'Success': 'Products uploaded.'}, status=200)

                except KeyError as er:
                    return JsonResponse({'Error': f'KeyError: {str(er)}'}, status=400)

        return JsonResponse({'Error': 'You should provide a URL'}, status=400)


class ListProductView(ListAPIView):
    queryset = ProductInfo.objects.select_related('product').prefetch_related('shop', 'product__category')
    serializer_class = ProductInfoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['model', 'product__name', 'shop__name', 'product__category__name']
    ordering_fields = ['model', 'product__name', 'shop__name', 'product__category__name', 'price_rrc', 'quantity']



class ListItemsOrder(ListAPIView):
    """
    List API View for Order Items.

    This view handles listing of order items for authenticated users.
    It filters the order items based on the user making the request.
    """
    permission_classes = [IsAuthenticated]
    queryset = OrderItem.objects.all()
    serializer_class = ListItemsSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['model', 'product__name', 'shop__name', 'product__category__name']
    ordering_fields = ['model', 'product__name', 'shop__name', 'product__category__name', 'price_rcc']

    def get_queryset(self):
        user = self.request.user
        return OrderItem.objects.filter(order__user=user, order__status='new').select_related('product')


class AddOrderItemView(CreateAPIView):
    """
    View for adding order items.

    This view handles the creation of new order items. It checks if the user is authenticated,
    validates the incoming data, and then creates or updates the order item accordingly.
    """
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user'] = self.request.user
        order, created = Order.objects.get_or_create(user=user, contact=serializer.validated_data['contact'], status='new')
        # an empty dict to store info about added products
        info = {}
        for item in serializer.validated_data['orderitem_set']:
            product_id = item.get('product').get('id')
            product = Product.objects.get(id=product_id)
            total_quantity = product.product_info.first().quantity
            item.pop('product')
            product_item = OrderItem.objects.filter(order=order, product=product).first()

            if product_item:
                if total_quantity < (item['quantity'] + product_item.quantity):
                    available_quantity = total_quantity - product_item.quantity
                    return Response({'Error': f'Not enough products in stock. '
                                                  f'There are {product.name}: available {available_quantity} pieces',
                                         **info},
                                        status=status.HTTP_403_FORBIDDEN)
                info[product.name] = 'added in order'
                product_item.quantity += item['quantity']
                product_item.save()
            else:
                if total_quantity < item['quantity']:
                    return Response({'Error': f'Not enough products in stock. '
                                                  f'There are {product.name}: available {total_quantity} pieces',
                                         **info},
                                        status=status.HTTP_403_FORBIDDEN)
                info[product.name] = 'added in order'
                product_item = OrderItem.objects.create(order=order, product=product, **item)

        return Response({"Success": "Item(s) added successfully"}, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        return context


class DeleteOrderItemView(DestroyAPIView):
    """
    View for deleting order items.

    This view handles the deletion of order items. It checks if the user is authenticated,
    validates the incoming data, and then deletes the order item accordingly.
    """
    permission_classes = [IsAuthenticated, IsOwnerOrderItem]
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    lookup_field = 'pk'


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"Success": "Item deleted successfully"},status=status.HTTP_204_NO_CONTENT)


class ListOrderView(ListAPIView):
    """
    List API View for Orders.

    This view handles listing of orders for authenticated users.
    It filters the orders based on the user making the request.
    """
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class = ListOrderSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user=user)


class DetailOrderView(RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrder]
    queryset = Order.objects.select_related('user', 'contact').prefetch_related('orderitem_set__product')
    serializer_class = GetOrderSerializer


class ConfirmOrderView(UpdateAPIView):
    """
    View for confirming order.

    This view handles the confirmation of an order. It checks if the user is authenticated,
    validates the incoming data, and then updates the order accordingly.
    """
    permission_classes = [IsAuthenticated, IsOwnerOrder]
    queryset = Order.objects.all()
    serializer_class = ConfirmOrderSerializer
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        if instance.status in ['confirmed', 'assembled', 'sent', 'delivered', 'canceled']:
            return Response({"Order status": f"{instance.status}"}, status=status.HTTP_403_FORBIDDEN)
        instance.status = 'confirmed'

        for item in instance.orderitem_set.all():
            product = item.product
            product_info = product.product_info.first()
            product_info.quantity -= item.quantity
            product_info.save()

        self.perform_update(instance)
        return Response({"Success": "Order confirmed successfully"},status=status.HTTP_200_OK)
