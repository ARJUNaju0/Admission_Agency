from django.urls import path, include
from . import views

urlpatterns = [
    # Template Views
    path('', views.college_list_view, name='college_list'),
    path('colleges/<int:college_id>/', views.college_detail_view, name='college_detail'),
    
    # API Views
    path('api/colleges/', views.CollegeListAPIView.as_view(), name='college-list-api'),
    path('api/colleges/<int:pk>/', views.CollegeDetailAPIView.as_view(), name='college-detail-api'),
    path('api/courses/', views.CourseListAPIView.as_view(), name='course-list-api'),
    path('api/stats/', views.college_stats_api, name='college-stats-api'),
]   
