from django.core.validators import URLValidator
from django.http import JsonResponse
from requests import get
from rest_framework import filters
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView

from yaml import Loader, load as load_yaml

from .models import (Shop, Category, Product, ProductInfo, Parameter, ProductParameter)
from .serializers import ProductInfoSerializer


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
    queryset = ProductInfo.objects.select_related('product').all()
    serializer_class = ProductInfoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['model', 'product__name', 'shop__name', 'product__category__name']
    ordering_fields = ['model', 'product__name', 'shop__name', 'product__category__name', 'price_rrc', 'quantity']
