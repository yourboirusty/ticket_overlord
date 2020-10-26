from stats.tests.core import StatTestCase
from event.models import AvailableTickets


class EventTestCase(StatTestCase):

    def test_sold_amount(self):
        reservation = self.reg_ticket1.reserve(user=self.users.pop(), amount=4)
        reservation.validated = True
        reservation.save()
        reservation = self.reg_ticket2.reserve(user=self.users.pop(), amount=4)
        reservation.validated = True
        reservation.save()
        self.vip_ticket1.reserve(user=self.users.pop(), amount=2)
        self.assertEqual(AvailableTickets.sold_amount('REG'), 8)

    def test_reservation_amount(self):
        self.reg_ticket1.reserve(user=self.users.pop(), amount=2)
        self.reg_ticket2.reserve(user=self.users.pop(), amount=4)
        self.vip_ticket1.reserve(user=self.users.pop(), amount=2)
        self.assertEqual(AvailableTickets.reservation_amount('REG'), 6)

    def test_reservation_avg_amount(self):
        self.reg_ticket1.reserve(user=self.users.pop(), amount=2)
        self.reg_ticket2.reserve(user=self.users.pop(), amount=4)
        self.vip_ticket1.reserve(user=self.users.pop(), amount=2)
        self.assertEqual(AvailableTickets.reservation_avg_amount('REG'), 3)

    def test_profit(self):
        reservation = self.reg_ticket1.reserve(user=self.users.pop(), amount=4)
        reservation.validated = True
        reservation.save()
        reservation = self.reg_ticket2.reserve(user=self.users.pop(), amount=4)
        reservation.validated = True
        reservation.save()
        reservation = self.vip_ticket1.reserve(user=self.users.pop(), amount=2)
        reservation.validated = True
        reservation.save()
        self.assertEqual(AvailableTickets.profit('REG'), 8*10)

