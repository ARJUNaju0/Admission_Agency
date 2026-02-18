from django.urls import path 
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin/login/', views.admin_login_view, name='admin_login'),
    path('admin/logout/', views.admin_logout_view, name='admin_logout'),
]