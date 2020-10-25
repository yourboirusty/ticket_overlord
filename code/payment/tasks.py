from celery import shared_task
from celery.result import AsyncResult
from event.tasks import remove_on_timeout
from payment.gateway import PaymentGateway
from payment.exceptions import (CardError,
                                PaymentError,
                                CurrencyError)
from django.apps import apps
from config.celery import app

gateway = PaymentGateway()

Payment = None


@shared_task
def process_payment(payment_id, amount, currency, token):
    global Payment
    if not Payment:
        Payment = apps.get_model('payment', 'Payment')
    payment = Payment.objects.get(pk=payment_id)
    payment.error = None
    try:
        payment.amount, payment.currency = gateway.charge(
            amount, currency, token)
    except (CardError, PaymentError, CurrencyError) as e:
        payment.error = str(e)
    payment.save()
