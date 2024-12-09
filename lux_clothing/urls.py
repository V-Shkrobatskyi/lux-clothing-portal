from rest_framework import routers

from lux_clothing.views import (
    ProfileViewSet,
    AddressViewSet,
)

app_name = "lux_clothing"

router = routers.DefaultRouter()
router.register("profiles", ProfileViewSet)
router.register("addresses", AddressViewSet)

urlpatterns = router.urls
