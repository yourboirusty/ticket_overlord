from django.db import models
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from django.utils.functional import cached_property
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.db.models import Sum, Avg
from django.conf import settings
from event.exceptions import EventStartedError, NotEnoughTicketsError


class Event(models.Model):
    name = models.CharField("Event name", max_length=50)
    date = models.DateField("Event date and time",
                            auto_now=False,
                            auto_now_add=False)

    class Meta:
        ordering = ['date']

    def can_reserve(self):
        return self.date > timezone.now()


class AvailableTickets(models.Model):
    TicketTypes = [
        ("VIP", "VIP"),
        ("REG", "Regular"),
        ("DIS", "Discounted")
    ]
    ticket_type = models.CharField("Ticket type",
                                   choices=TicketTypes,
                                   max_length=3)
    event = models.ForeignKey("Event",
                              verbose_name="Event",
                              related_name="tickets",
                              on_delete=models.CASCADE)
    price = models.IntegerField("Price in EUR")
    amount = models.IntegerField("Pool of tickets")

    @cached_property
    def reservation_amount(self):
        time_delta = timezone.now() - timedelta(minutes=15)
        query = Q(created__gte=time_delta) | Q(validated=True)
        reserved = self.reservations.filter(query).aggregate(Sum('amount'))
        amount = reserved.get('amount__sum')
        if not amount:
            amount = 0
        return amount

    @cached_property
    def available(self):
        reserved = self.reservation_amount
        return self.amount - reserved

    @cached_property
    def reservation_avg_amount(self):
        time_delta = timezone.now() - timedelta(minutes=15)
        query = Q(created__gte=time_delta) | Q(validated=True)
        reserved = self.reservations.filter(query).aggregate(Avg('amount'))
        avg = reserved.get('amount__avg')
        if not avg:
            avg = 0
        return avg

    @cached_property
    def reservation_count(self):
        time_delta = timezone.now() - timedelta(minutes=15)
        return self.reservations.filter(created__gte=time_delta).count()

    def reload_reservation_cache(self):
        for key in ['reservation_amount',
                    'available',
                    'reservation_avg_amount',
                    'reservation_count']:
            if key in self.__dict__:
                del self.__dict__[key]

    def reserve(self, user, amount=1, *, created=None):
        if not created:
            created = timezone.now()
        reservation = Reservation(
            client=user,
            ticket_type=self,
            amount=amount,
            created=created
        )
        reservation.save()
        return reservation


class Reservation(models.Model):
    client = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.CASCADE)
    created = models.DateTimeField("Reservation creation datetime",
                                   auto_now_add=True)
    ticket_type = models.ForeignKey("AvailableTickets",
                                    related_name="reservations",
                                    verbose_name="Ticket that's reserved",
                                    on_delete=models.CASCADE)
    amount = models.IntegerField(default=1)
    validated = models.BooleanField("Reservation paid", default=False)

    class Meta:
        unique_together = ['client', 'ticket_type']
        ordering = ['created']

    def check_validity(self):
        """Check if reservation is still valid
        """
        time_delta = timezone.now() - timedelta(minutes=15)
        if self.created > time_delta or self.validated:
            return True
        return False


@receiver(pre_save, sender=Reservation)
def validate_reservation(sender, instance, *args, **kwargs):
    if not instance.ticket_type.event.can_reserve():
        raise EventStartedError("{0} has started already.".format(
            instance.ticket_type.event
        ))
    if instance.ticket_type.available < instance.amount:
        raise NotEnoughTicketsError(
            "Trying to reserve {0}, only {1} available".format(
                instance.amount, instance.ticket_type.available
            ))


@receiver([post_save], sender=Reservation)
def reset_cache(sender, instance, created, *args, **kwargs):
    instance.ticket_type.reload_reservation_cache()
