from stats.views import EventStatsViewset, TicketStatsViewset
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'events', EventStatsViewset, basename='stat-event')
router.register(r'tickets', TicketStatsViewset, basename='stat-ticket')

urlpatterns = router.urls
