from rest_framework import routers

from lux_clothing.views import (
    ProfileViewSet,
    AddressViewSet,
    CategoryViewSet,
    BrandViewSet,
    SizeViewSet,
    ProductHeadViewSet,
    ColorViewSet,
)

app_name = "lux_clothing"

router = routers.DefaultRouter()
router.register("profiles", ProfileViewSet)
router.register("addresses", AddressViewSet)
router.register("categories", CategoryViewSet)
router.register("brands", BrandViewSet)
router.register("sizes", SizeViewSet)
router.register("products_head", ProductHeadViewSet)
router.register("products_photo", ProductPhotoViewSet)

urlpatterns = router.urls
