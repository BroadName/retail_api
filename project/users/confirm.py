from django.conf import settings
from django.core.mail import EmailMessage


def send_email(email, token, recipient):

    link = f'http://127.0.0.1:8000/api/v1/confirm_email/{token}/{email}'
    body = f"""
            Please click on the link to confirm your email:
            <a href="{link}">Confirm your email</a>
            """
    msg = EmailMessage('Registration on retail site',
                       body, settings.EMAIL_HOST_USER, recipient)
    msg.content_subtype = "html"
    msg.send()


def send_confirmed_order(order_info, recipient):

    products_list = ""

    for product, details in order_info['products'].items():
        products_list += f"{product} x {details['quantity']}, total price: {details['total price']}, product_id: {details['id']}\n"

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
    msg_to_user.send()

    msg_to_admin = EmailMessage('Registration on retail site',
                       body_to_admin, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER])
    msg_to_admin.content_subtype = "html"
    msg_to_admin.send()