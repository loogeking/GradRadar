from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    MajorViewSet,
    ScoreLineViewSet,
    EnrollmentViewSet,
    ReferenceBookViewSet,
    CompareView,
    TrendView,
)

router = DefaultRouter()
router.register(r'majors', MajorViewSet, basename='major')
router.register(r'scorelines', ScoreLineViewSet, basename='scoreline')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')
router.register(r'reference-books', ReferenceBookViewSet, basename='reference-book')

urlpatterns = router.urls + [
    path('compare/', CompareView.as_view(), name='compare'),
    path('trends/<int:major_id>/', TrendView.as_view(), name='trends'),
]