from celery import shared_task
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from requests import get
from yaml import load as load_yaml, Loader
from django.db import IntegrityError
from .models import Shop, Category, Product, ProductInfo, Parameter, ProductParameter
from django.conf import settings
from django.core.mail import EmailMessage


@shared_task(bind=True)
def upload_products(self, user_id, url):
    try:
        validate = URLValidator()
        validate(url)
    except ValidationError as er:
        return JsonResponse({'Error': str(er)}, status=400)

    stream = get(url).content
    data = load_yaml(stream, Loader=Loader)

    try:
        shop, created = Shop.objects.get_or_create(
            name=data['shop'],
            user_id=user_id
        )

        for category in data.get('categories'):
            category_obj, created = Category.objects.get_or_create(
                external_id=category['id'],
                name=category['name']
            )
            category_obj.shops.set([shop.id])

        for product in data.get('goods'):
            product_obj, created = Product.objects.get_or_create(
                name=product['name'],
                category=Category.objects.get(external_id=product['category'])
            )

            try:
                product_info_obj, created = ProductInfo.objects.get_or_create(
                    product=product_obj,
                    model=product['model'],
                    external_id=product['id'],
                    shop=shop,
                    quantity=product['quantity'],
                    price=product['price'],
                    price_rrc=product['price_rrc']
                )

            except IntegrityError:
                continue

            for key, value in product['parameters'].items():
                parameter_obj, created = Parameter.objects.get_or_create(
                    name=key
                )

                product_parameter_obj, created = ProductParameter.objects.get_or_create(
                    product_info=product_info_obj,
                    parameter=parameter_obj,
                    value=value
                )

        return {'Success': 'Products uploaded.'}

    except KeyError as er:
        return JsonResponse({'Error': f'KeyError: {str(er)}'}, status=400)


@shared_task
def send_confirmed_order(order_info, recipient):

    products_list = ""

    for product, details in order_info['products'].items():
        products_list += f"{product} x {details['quantity']}, total price: {details['total price']}, product_item_id: {details['id']}\n"

    body_to_recipient = f"""
    <pre>
    You have confirmed your order #{order_info['order_id']}.
    Your products:
{products_list}
    Order price = {order_info['price_order']}
    Thank you for your choice! Have a nice day!
    </pre>
                """

    body_to_admin = f"""
    <pre>
    User {order_info['user']} has confirmed order #{order_info['order_id']}.
    Products:
{products_list}
    Price order = {order_info['price_order']}
    </pre>
                """

    msg_to_user = EmailMessage('Registration on retail site',
                       body_to_recipient, settings.EMAIL_HOST_USER, recipient)
    msg_to_user.content_subtype = "html"
    # try:
    msg_to_user.send()

    msg_to_admin = EmailMessage('Registration on retail site',
                                body_to_admin, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER])
    msg_to_admin.content_subtype = "html"
    msg_to_admin.send()

    return {"Success": "Order confirmed successfully"}