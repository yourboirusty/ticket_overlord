from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from event.models import Event, AvailableTickets
from django.contrib.auth import get_user_model

User = get_user_model()
now = timezone.now()


class StatTestCase(TestCase):

    def test_setUp(self):
        self.tickets = [self.vip_ticket1,
                        self.vip_ticket2,
                        self.reg_ticket1,
                        self.reg_ticket2]

        for ticket in self.tickets:
            for user in self.users:
                res = ticket.reserve(user=user, amount=randint(2, 15))
                if randint(0, 1):
                    res.validated = True
                    res.save()

        self.expected_values = list()
        self.events = [self.event1, self.event2]
        for event in self.events:
            results = {
                'event': str(event),
                'reservation_amount': event.reservation_amount,
                'sold_amount': event.sold_amount,
                'profit': event.profit,
            }
            self.expected_values.append(results)

    def additional_setUp(self):
        pass

    def setUp(self):
        self.event1 = Event.objects.create(name="Test Event",
                                           date=timezone.now() +
                                           timedelta(days=150))

        self.event2 = Event.objects.create(name="Test Event2",
                                           date=timezone.now() +
                                           timedelta(days=160))

        self.vip_ticket1 = AvailableTickets.objects.create(
            ticket_type='VIP',
            event=self.event1,
            price=15,
            amount=100
        )

        self.vip_ticket2 = AvailableTickets.objects.create(
            ticket_type='VIP',
            event=self.event2,
            price=15,
            amount=100
        )

        self.reg_ticket1 = AvailableTickets.objects.create(
            ticket_type='REG',
            event=self.event1,
            price=10,
            amount=100
        )

        self.reg_ticket2 = AvailableTickets.objects.create(
            ticket_type='REG',
            event=self.event2,
            price=10,
            amount=100
        )

        self.users = list()
        for n in range(6):
            self.users.append(
                User.objects.create_user(username="user"+str(n),
                                         password="pwd"+str(n))
            )
        self.additional_setUp()
