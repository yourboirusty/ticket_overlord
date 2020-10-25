from django.test import TransactionTestCase
from django.utils import timezone
from datetime import timedelta
from payment.models import Payment
from event.models import Event, AvailableTickets, Reservation
from payment import tasks
from celery.contrib.testing.worker import start_worker
from config.celery import app
from django.contrib.auth import get_user_model
from unittest import skip

User = get_user_model()


class PaymentTestCase(TransactionTestCase):
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
        super().setUp()
        self.event = Event.objects.create(name="Test Event",
                                          date=timezone.now() +
                                          timedelta(days=50))
        self.ticket = AvailableTickets.objects.create(
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
            ticket_type=self.ticket,
            amount=2
        )
        self.payment = Payment.objects.create(reservation=self.reservation)

    def test_price_calc(self):
        self.assertEqual(self.payment.full_price, 30)

    @skip("Celery testing problems")
    def test_pay(self):
        """Celery doesn't have access to test database (despite working on
        the model tests perfectly with this configuration).
        """
        res = tasks.process_payment.delay(self.payment.id, 30, 'EUR', 'ok')
        returns = res.get()
        self.assertEqual(returns.status, 'SUCCESS')
