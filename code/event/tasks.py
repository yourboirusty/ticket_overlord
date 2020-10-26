from celery import shared_task
from django.apps import apps
from time import sleep

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
    if reservation.payment:
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
