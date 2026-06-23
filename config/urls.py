from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # API 路由
    path('api/', include('apps.schools.urls')),
    path('api/', include('apps.majors.urls')),
    path('api/', include('apps.tutors.urls')),
    path('api/', include('apps.notices.urls')),
    path('api/', include('apps.subjects.urls')),
    path('api/user/', include('apps.users.urls')),
    path('api-auth/', include('rest_framework.urls')),

    # 前端页面（必须放最后，因为''匹配根路径）
    path('', include('apps.frontend.urls')),
]