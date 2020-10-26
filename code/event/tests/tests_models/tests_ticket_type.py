from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from event.models import Event, AvailableTickets
from django.contrib.auth import get_user_model
import mock

User = get_user_model()
now = timezone.now()


class AvailableTicketsTestCase(TestCase):
    @mock.patch('django.utils.timezone.now',
                lambda: now - timedelta(minutes=30))
    def setUp(self):
        self.event = Event.objects.create(name="Test Event",
                                          date=timezone.now() +
                                          timedelta(days=150))
        self.av_ticket = AvailableTickets.objects.create(
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

    def test_cache_reload(self):
        self.assertEqual(self.av_ticket.available, 100)
        self.av_ticket.amount = 40
        self.av_ticket.save()
        self.assertEqual(self.av_ticket.available, 100)
        self.av_ticket.reload_reservation_cache()
        self.assertEqual(self.av_ticket.available, 40)

    def test_reserve(self):
        self.assertEqual(self.av_ticket.reservations.count(), 0)
        reservation = self.av_ticket.reserve(self.users.pop())
        self.assertIsNotNone(reservation.id)
        self.assertEqual(self.av_ticket.reservations.count(), 1)
        reservation = self.av_ticket.reserve(self.users.pop(), amount=2)
        self.assertEqual(self.av_ticket.reservations.count(), 2)

    def test_check_available(self):
        self.assertEqual(self.av_ticket.available, 100)
        self.av_ticket.reserve(amount=2, user=self.users.pop())
        self.assertEqual(self.av_ticket.available, 98)
