from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import BookingViewSet, RegisterView, RoomViewSet, current_user

router = DefaultRouter()
router.register(r"rooms", RoomViewSet)
router.register(r"bookings", BookingViewSet)

urlpatterns = router.urls

urlpatterns += [
    path("register/", RegisterView.as_view(), name="register"),
    path("users/me/", current_user)
]
