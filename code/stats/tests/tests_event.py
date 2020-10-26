from stats.tests.core import StatTestCase


class EventTestCase(StatTestCase):

    def test_reservation_amount(self):
        self.reg_ticket1.reserve(user=self.users.pop(), amount=4)
        self.vip_ticket1.reserve(user=self.users.pop(), amount=2)
        self.assertEqual(self.event1.reservation_amount, 6)

    def test_sold_amount(self):
        reservation = self.reg_ticket1.reserve(user=self.users.pop(), amount=4)
        reservation.validated = True
        reservation.save()
        self.vip_ticket1.reserve(user=self.users.pop(), amount=2)
        self.assertEqual(self.event1.sold_amount, 4)

    def test_profit(self):
        reservation = self.reg_ticket1.reserve(user=self.users.pop(), amount=4)
        reservation.validated = True
        reservation.save()
        self.vip_ticket1.reserve(user=self.users.pop(), amount=2)
        self.assertEqual(self.event1.profit, 4*10)
