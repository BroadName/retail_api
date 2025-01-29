import smtplib
from datetime import timedelta


from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)

from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMessage
from celery import shared_task
from users.models import ConfirmToken


@shared_task
def send_email(email:str, token:str, recipient:list) -> dict:

    """
    This function sends a confirmation email to the user.
    """

    link = f'http://127.0.0.1:8000/api/v1/confirm_email/{token}/{email}'
    body = f"""
            Please click on the link to confirm your email:
            <a href="{link}">Confirm your email</a>
            If you did not request this, please ignore this email
            """
    msg = EmailMessage('Registration on retail site',
                       body, settings.EMAIL_HOST_USER, recipient)
    msg.content_subtype = "html"

    try:
        msg.send()
        logger.info(f"Email sent successfully to {recipient}")
        return {'success': 'Email sent successfully'}

    except smtplib.SMTPDataError as e:
        logger.error(f"SMTPDataError: {e} for recipient: {recipient}")
        return {"Error": str(e)}

    except smtplib.SMTPException as e:
        logger.error(f"SMTPException: {e} for recipient: {recipient}")
        return {"Error": str(e)}


@shared_task
def check_email_verification():
    tokens = ConfirmToken.objects.all()

    for token in tokens:
        user_token = cache.get(f'token_{token.user.id}')
        user_email = cache.get(f'user_email_{token.user.id}')
        if (timezone.now() - token.dt) > timedelta(minutes=5):
            logger.info(f"{user_email} verification failed for user id={token.user.id}. \n"
                        f" Token - {user_token} is expired.")
            token.delete()
            cache.delete(f'token_{token.user.id}')
            cache.delete(f'user_email_{token.user.id}')
        else:
            logger.info(f"{user_email} is waiting for confirmation for user id={token.user.id}. \n"
                    f" Token - {user_token} is valid.")