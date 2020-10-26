from django.db import models
from django.utils.functional import cached_property
from payment.tasks import process_payment
from payment.exceptions import MissingReservation, InvalidReservation
from celery.result import AsyncResult


class Payment(models.Model):
    reservation = models.ForeignKey('event.Reservation',
                                    on_delete=models.CASCADE,
                                    related_name='payment',
                                    null=True)
    payment_id = models.CharField("Celery task ID for payment processing",
                                  max_length=256,
                                  null=True)
    amount = models.IntegerField("Amount paid", null=True)
    currency = models.CharField("Currency", max_length=3, null=True)
    error = models.CharField("Errors that occured", max_length=256, null=True)

    @cached_property
    def full_price(self):
        return self.reservation.amount * self.reservation.ticket_type.price

    def payment_status(self):
        if not self.payment_id:
            return "NOT_STARTED"
        res = AsyncResult(self.payment_id)
        return res.status

    def pay(self, amount, token, currency):
        if not self.reservation:
            raise MissingReservation("Your reservation has timed out and was \
                removed")
        if not self.reservation.check_validity():
            raise InvalidReservation("Your reservation has timed out")
        self.payment_id = process_payment.delay(self.id,
                                                amount,
                                                currency,
                                                token).id
        self.save()
