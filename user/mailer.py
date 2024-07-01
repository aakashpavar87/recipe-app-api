from django.conf import settings
from django.core.mail import send_mail


def send_email_to_customer(to, subject, msg):
    from_email = settings.EMAIL_HOST_USER
    send_mail(subject, msg, from_email, to)
