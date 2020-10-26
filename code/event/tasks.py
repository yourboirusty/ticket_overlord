from celery import shared_task
from django.apps import apps
from time import sleep
from django.core.exceptions import ObjectDoesNotExist

Reservation = None


@shared_task
def remove_on_timeout(reservation_id):
    global Reservation
    if not Reservation:
        Reservation = apps.get_model('event', 'Reservation')
    reservation = Reservation.objects.get(pk=reservation_id)
    if reservation.validated:
        raise Exception("Reservation paid")
    # Handle payment in process
    has_payment = False
    try:
        has_payment = (reservation.payment is not None)
    except ObjectDoesNotExist:
        pass
    if has_payment:
        status = reservation.payment.payment_status()
        while status != 'SUCCESS':
            if status == 'NOT_STARTED':
                break
            if status == 'FAILED':
                break
            sleep(1)
            status = reservation.payment.payment_status()
            if status == 'SUCCESS':
                return False
    reservation.delete()
    return True
