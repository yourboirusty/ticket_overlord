from celery import shared_task
from django.apps import apps
import logging

Reservation = None


@shared_task
def remove_on_timeout(reservation_id):
    global Reservation
    if not Reservation:
        Reservation = apps.get_model('event', 'Reservation').objects
    reservation = Reservation.get(pk=reservation_id)
    if reservation.payment.count():
        raise Exception("Reservation during payment")
    reservation.delete()
    return True
