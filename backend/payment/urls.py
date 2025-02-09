from rest_framework import routers

from payment.views import (
    PaymentViewSet,
)

app_name = "payment"

router = routers.DefaultRouter()
router.register("", PaymentViewSet)

urlpatterns = router.urls
