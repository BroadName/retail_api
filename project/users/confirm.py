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