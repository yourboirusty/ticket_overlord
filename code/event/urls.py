from rest_framework import routers
from event.views import EventViewset

router = routers.SimpleRouter()
router.register(r'events', EventViewset)

urlpatterns = router.urls
