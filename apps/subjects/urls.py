from rest_framework.routers import DefaultRouter
from .views import SubjectViewSet, SubjectRatingViewSet

router = DefaultRouter()
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'subject-ratings', SubjectRatingViewSet, basename='subject-rating')

urlpatterns = router.urls