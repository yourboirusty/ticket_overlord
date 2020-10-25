from rest_framework import routers
from event.views import EventViewset, TicketStatusViewset, ReservationViewset

router = routers.SimpleRouter()
router.register(r'events', EventViewset)
router.register(r'tickets', TicketStatusViewset)
router.register(r'reservations', ReservationViewset)

urlpatterns = router.urls
