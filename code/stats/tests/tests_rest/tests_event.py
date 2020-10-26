from stats.tests.core import StatTestCase
from rest_framework.test import APIClient
from random import randint
from django.urls import reverse


class TestEventViewset(StatTestCase):
    def additional_setUp(self):

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

    def test_list_response(self):
        client = APIClient()
        response = self.client.get(reverse('stat-event-list'))
        self.assertEqual(response.status_code, 200)
        result = response.data[0]
        self.assertCountEqual(
            result.keys(),
            self.expected_values[0].keys()
        )
        for key, value in self.expected_values[0].items():
            self.assertEqual(result[key], value)

    def test_top_profit(self):
        client = APIClient()
        response = self.client.get(reverse('stat-event-top-profit'))
        self.assertEqual(response.status_code, 200)
        sorted_events = list(
            sorted(
                self.events,
                key=lambda x: x.profit
                )
            )

        self.assertEqual(response.data[0]['profit'],
                         sorted_events[0].profit)

    def test_top_popular(self):
        client = APIClient()
        response = self.client.get(reverse('stat-event-top-popular'))
        self.assertEqual(response.status_code, 200)
        sorted_events = list(
            sorted(
                [self.event1, self.event2],
                key=lambda x: x.reservation_amount
                )
            )
        self.assertEqual(response.data[0]['reservation_amount'],
                         sorted_events[0].reservation_amount)

    def test_top_selling(self):
        client = APIClient()
        response = self.client.get(reverse('stat-event-top-selling'))
        self.assertEqual(response.status_code, 200)
        sorted_events = list(
            sorted(
                [self.event1, self.event2],
                key=lambda x: x.sold_amount
                )
            )
        self.assertEqual(response.data[0]['sold_amount'],
                         sorted_events[0].sold_amount)


