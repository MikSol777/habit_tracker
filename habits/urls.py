from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import HabitViewSet, PublicHabitListView

router = DefaultRouter()
router.register("", HabitViewSet, basename="habit")

urlpatterns = [
    path("public/", PublicHabitListView.as_view(), name="public-habits"),
    path("", include(router.urls)),
]
