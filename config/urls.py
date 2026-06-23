from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # API 路由
    path('api/', include('apps.schools.urls')),
    path('api/', include('apps.majors.urls')),
    path('api/', include('apps.tutors.urls')),
    path('api/', include('apps.notices.urls')),
    path('api/user/', include('apps.users.urls')),

    # DRF登录界面（方便测试）
    path('api-auth/', include('rest_framework.urls')),
]