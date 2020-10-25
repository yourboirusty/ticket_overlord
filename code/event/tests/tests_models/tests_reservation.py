from django.test import TransactionTestCase
from unittest import skip
from django.utils import timezone
from datetime import timedelta
from event.models import Event, AvailableTickets, Reservation
from event.exceptions import EventStartedError, NotEnoughTicketsError
from event.tasks import remove_on_timeout
from celery.result import AsyncResult
from django.contrib.auth import get_user_model
from celery.contrib.testing.worker import start_worker
from config.celery import app


User = get_user_model()
now = timezone.now()


class AvailableTicketsTestCase(TransactionTestCase):
    allow_database_queries = True

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        app.loader.import_module('celery.contrib.testing.tasks')
        cls.celery_worker = start_worker(app)
        cls.celery_worker.__enter__()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.celery_worker.__exit__(None, None, None)

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

    def test_purge_task_creation(self):
        self.assertIsNotNone(self.reservation.purge_id)
        res = AsyncResult(self.reservation.purge_id)
        self.assertIsNotNone(res.id)

    def test_purge_task_revoke_on_delete(self):
        purge_id = self.reservation.purge_id
        self.reservation.delete()
        celery_inspect = app.control.inspect()
        revoked = list(celery_inspect.revoked().values())
        removed = False
        for table in revoked:
            if purge_id in table:
                removed = True
        self.assertTrue(removed)

    @skip("Got borked after requirements update")
    def test_purge_task_completion(self):
        res = AsyncResult(self.reservation.purge_id)
        res.revoke()
        res = remove_on_timeout.apply_async((self.reservation.id,),
                                            countdown=2)
        res = res.get()
        with self.assertRaises(Reservation.DoesNotExist):
            self.reservation.refresh_from_db()
        self.assertEqual(self.normal_ticket.available, 100)

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
