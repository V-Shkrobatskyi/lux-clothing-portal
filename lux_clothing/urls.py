from rest_framework import routers

from lux_clothing.views import (
    ProfileViewSet,
)

app_name = "lux_clothing"

router = routers.DefaultRouter()
router.register("profiles", ProfileViewSet)

urlpatterns = router.urls
