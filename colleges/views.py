from django.shortcuts import render, get_object_or_404
from rest_framework import generics, filters, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .models import College, Course
from .serializers import CollegeListSerializer, CollegeDetailSerializer, CourseSerializer

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny

# Template Views (Keep existing for web interface)
def college_list_view(request):
    return render(request, 'colleges/college_list.html')

def college_detail_view(request, college_id):
    college = get_object_or_404(College, id=college_id)
    context = {
        'college': college,
    }
    return render(request, 'colleges/college_detail.html', context)


# API Views
class CollegeListAPIView(generics.ListAPIView):
    """API endpoint for college listings"""
    
    queryset = College.objects.filter(is_active=True)
    serializer_class = CollegeListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['city', 'college_type', 'accreditation']
    search_fields = ['name', 'description', 'short_description', 'affiliated_to']
    ordering_fields = ['name', 'overall_rating', 'placement_percentage', 'average_package', 'nirf_rank']
    ordering = ['-is_featured', '-overall_rating', 'name']


class CollegeDetailAPIView(generics.RetrieveAPIView):
    """API endpoint for college details"""
    
    queryset = College.objects.filter(is_active=True)
    serializer_class = CollegeDetailSerializer
    lookup_field = 'id'


class CourseListAPIView(generics.ListAPIView):
    """API endpoint for course listings"""
    
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['college', 'level', 'stream']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'per_year_fees', 'total_fees', 'duration_years']
    ordering = ['college', 'level', 'name']
    
    def get_queryset(self):
        queryset = Course.objects.filter(is_active=True)
        college_id = self.request.query_params.get('college_id')
        if college_id:
            queryset = queryset.filter(college_id=college_id)
        return queryset


@api_view(['GET'])
@permission_classes([AllowAny])
def college_stats_api(request):
    """API endpoint for college statistics"""
    
    stats = {
        'total_colleges': College.objects.filter(is_active=True).count(),
        'colleges_by_city': [
            {'city': choice[0], 'count': College.objects.filter(is_active=True, city=choice[0]).count()}
            for choice in College.CITY_CHOICES
        ],
        'colleges_by_type': [
            {'type': choice[0], 'count': College.objects.filter(is_active=True, college_type=choice[0]).count()}
            for choice in College.TYPE_CHOICES
        ],
        'featured_colleges': CollegeListSerializer(
            College.objects.filter(is_active=True, is_featured=True)[:5], 
            many=True
        ).data,
        'top_rated_colleges': CollegeListSerializer(
            College.objects.filter(is_active=True).order_by('-overall_rating')[:5], 
            many=True
        ).data,
    }
    
    return Response(stats)

# def college_compare_view(request):
#     return render(request, 'colleges/college_compare.html')