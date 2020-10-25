from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from event.models import Event


class EventTestCase(TestCase):
    def setUp(self):
        self.event = Event.objects.create(name="Test Event",
                                          date=timezone.now())

    def test_reservation_block(self):
        self.event.date = (timezone.now() + timedelta(minutes=15))
        self.event.save()
        self.assertTrue(self.event.can_reserve())
        self.event.date = (timezone.now() - timedelta(minutes=15))
        self.event.save()
        self.assertFalse(self.event.can_reserve())
