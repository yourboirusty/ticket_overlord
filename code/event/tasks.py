from celery import shared_task
from django.apps import apps

Reservation = None


@shared_task
def remove_on_timeout(reservation_id):
    global Reservation
    if not Reservation:
        Reservation = apps.get_model('event', 'Reservation')
    reservation = Reservation.objects.get(pk=reservation_id)
    if reservation.payment.count():
        if not reservation.payment.error:
            raise Exception("Reservation during payment")
    reservation.delete()
    return True
