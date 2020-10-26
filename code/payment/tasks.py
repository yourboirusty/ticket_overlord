from celery import shared_task
from celery.result import AsyncResult
from payment.gateway import PaymentGateway
from payment.exceptions import (CardError,
                                PaymentError,
                                CurrencyError)
from django.apps import apps

gateway = PaymentGateway()

Payment = None


@shared_task
def process_payment(payment_id, amount, token, currency='EUR'):
    global Payment
    if not Payment:
        Payment = apps.get_model('payment', 'Payment')
    payment = Payment.objects.get(pk=payment_id)
    payment.error = None
    try:
        payment.amount, payment.currency = gateway.charge(
            amount=amount, token=token, currency=currency)
        payment.reservation.validated = True
        res = AsyncResult(payment.reservation.purge_id)
        res.revoke()
        payment.reservation.purge_id = None
        payment.reservation.save()
        payment.save()
    except (CardError, PaymentError, CurrencyError) as e:
        payment.error = str(e)
        payment.save()
        raise Exception('Payment error')
