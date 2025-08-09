from celery import shared_task
from django.core.mail import send_mail, BadHeaderError
from smtplib import SMTPException
import socket
from random import randint
from django.core.cache import cache
from django.conf import settings


def generate_code():
    str_result = "".join(str(randint(1, 9)) for _ in range(7))
    return int(str_result)


@shared_task
def send_account_confirmation_email(receiver):
    code = generate_code()
    key = f"mailkey:{receiver}"
    stored_key = cache.get(key)
    if stored_key:
        return False
    
    try:
        send_mail(
            "Verification code",
            f"Your verification code is {code}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[receiver]
        )
        # Store sent keys in redis with a short TTL
        cache.set(key, code, timeout=5*60)

        return {"key": key}
    except SMTPException as e:
        print(f"SMTP error occurred: {e}")
    except BadHeaderError:
        print("Invalid email header.")
    except socket.error as e:
        print(f"Network error: {e}")