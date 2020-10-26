from stats.tests.core import StatTestCase
from event.models import Event

if not Event.objects.all().count():
    init = StatTestCase()
    init.setUp()
    init.test_setUp()
