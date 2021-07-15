import logging

from celery import shared_task
from django.core.mail import EmailMessage
from django.template import loader

logger = logging.getLogger("celery")


@shared_task(bind=True, max_retries=3)
def send_email(self, subject, context, template, recipients):
    """Async task to send an email to user."""
    body = loader.render_to_string(template, context)
    email = EmailMessage(
        subject, body, to=recipients
    )

    email.content_subtype = 'html'
    try:
        logger.info(f"Sending email to '{recipients}'")
        email.send(fail_silently=False)
        logger.info(f"Email notification sent to {recipients}.")
    except ConnectionError as exc:
        self.retry(exc=exc, countdown=180)
        logger.error(f"Email to {recipients} timeout error!")
