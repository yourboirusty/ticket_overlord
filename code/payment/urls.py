from rest_framework import routers
from payment.views import PaymentViewset

router = routers.SimpleRouter()
router.register(r'payments', PaymentViewset)

urlpatterns = router.urls