from rest_framework.routers import DefaultRouter
from .views import ProvinceViewSet, SchoolViewSet, CollegeViewSet

router = DefaultRouter()
router.register(r'provinces', ProvinceViewSet, basename='province')
router.register(r'schools', SchoolViewSet, basename='school')
router.register(r'colleges', CollegeViewSet, basename='college')

urlpatterns = router.urls