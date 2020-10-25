from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from event.models import Event, AvailableTickets, Reservation
from event.exceptions import EventStartedError, NotEnoughTicketsError
from django.contrib.auth import get_user_model
import mock


User = get_user_model()
now = timezone.now()


class AvailableTicketsTestCase(TestCase):

    @mock.patch('django.utils.timezone.now',
                lambda: now - timedelta(minutes=30))
    def make_old_reservation(self, amount=3,
                             ticket_type=0):
        self.old_reservation = Reservation.objects.create(
            ticket_type=ticket_type,
            client=self.users.pop(),
            amount=amount
        )

    def setUp(self):
        self.event = Event.objects.create(name="Test Event",
                                          date=now +
                                          timedelta(days=50))
        self.vip_ticket = AvailableTickets.objects.create(
            ticket_type='VIP',
            event=self.event,
            price=15,
            amount=100
        )
        self.normal_ticket = AvailableTickets.objects.create(
            ticket_type='VIP',
            event=self.event,
            price=15,
            amount=100
        )
        self.users = list()
        for n in range(6):
            self.users.append(
                User.objects.create_user(username="user"+str(n),
                                         password="pwd"+str(n))
            )
        self.reservation = Reservation.objects.create(
            client=self.users.pop(),
            ticket_type=self.normal_ticket,
            amount=2
        )
        self.make_old_reservation(ticket_type=self.vip_ticket)

    def test_timeout_checking(self):
        self.assertTrue(self.reservation.check_validity())
        self.assertFalse(self.old_reservation.check_validity())
        self.old_reservation.validated = True
        self.old_reservation.save()
        self.assertTrue(self.old_reservation.check_validity())

    def test_event_started(self):
        self.event.date = now - timedelta(days=1)
        self.event.save()
        with self.assertRaises(EventStartedError):
            self.reservation.save()

    def test_no_more_tickets(self):
        self.normal_ticket.amount = 0
        self.normal_ticket.save()
        with self.assertRaises(NotEnoughTicketsError):
            self.reservation.save()
