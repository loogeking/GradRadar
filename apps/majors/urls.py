from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    MajorViewSet,
    ResearchDirectionViewSet,
    ScoreLineViewSet,
    EnrollmentViewSet,
    ReferenceBookViewSet,
    NationalScoreLineViewSet,
    CompareView,
    TrendView,
)

router = DefaultRouter()
router.register(r'majors', MajorViewSet, basename='major')
router.register(r'research-directions', ResearchDirectionViewSet, basename='research-direction')
router.register(r'scorelines', ScoreLineViewSet, basename='scoreline')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')
router.register(r'reference-books', ReferenceBookViewSet, basename='reference-book')
router.register(r'national-lines', NationalScoreLineViewSet, basename='national-line')

urlpatterns = router.urls + [
    path('compare/', CompareView.as_view(), name='compare'),
    path('trends/<int:major_id>/', TrendView.as_view(), name='trends'),
]