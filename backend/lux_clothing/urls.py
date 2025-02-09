from rest_framework import routers

from lux_clothing.views import (
    ProfileViewSet,
    AddressViewSet,
    CategoryViewSet,
    BrandViewSet,
    SizeViewSet,
    ProductHeadViewSet,
    ColorViewSet,
    ProductPhotoViewSet,
    ProductViewSet,
    OrderItemViewSet,
    OrderViewSet,
    ForWhomViewSet,
    StyleViewSet,
)

app_name = "lux_clothing"

router = routers.DefaultRouter()
router.register("profiles", ProfileViewSet)
router.register("addresses", AddressViewSet)
router.register("categories", CategoryViewSet)
router.register("brands", BrandViewSet)
router.register("for_whom", ForWhomViewSet)
router.register("styles", StyleViewSet)
router.register("sizes", SizeViewSet)
router.register("products_head", ProductHeadViewSet)
router.register("products_photo", ProductPhotoViewSet)
router.register("colors", ColorViewSet)
router.register("products", ProductViewSet)
router.register("order_items", OrderItemViewSet)
router.register("orders", OrderViewSet)

urlpatterns = router.urls
