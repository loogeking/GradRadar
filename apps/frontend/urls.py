from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('schools/', views.school_list, name='school_list'),
    path('schools/<int:pk>/', views.school_detail, name='school_detail'),
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/<int:pk>/', views.subject_detail, name='subject_detail'),
    path('majors/<int:pk>/', views.major_detail, name='major_detail'),
    path('search/', views.search, name='search'),
    path('compare/', views.compare, name='compare'),
    path('login/', views.login_page, name='login_page'),
    path('register/', views.register_page, name='register_page'),
    path('favorites/', views.favorites, name='favorites'),
]