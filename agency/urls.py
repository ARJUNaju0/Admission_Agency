from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.agent_dashboard, name='admin_dashboard'),
    path('inquiry/<int:inquiry_id>/', views.inquiry_detail, name='inquiry_detail'),
    path('submit/<int:college_id>/', views.create_inquiry, name='create_inquiry'),
]