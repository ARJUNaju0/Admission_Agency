from rest_framework import serializers
from .models import College, Course, Facility, CollegeReview

class FacilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Facility
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    college_name = serializers.CharField(source='college.name', read_only=True)
    
    class Meta:
        model = Course
        fields = [
            'id', 'college', 'college_name', 'name', 'level', 'stream',
            'duration_years', 'total_fees', 'per_year_fees', 'seats_available',
            'eligibility', 'entrance_exams', 'description', 'syllabus',
            'is_active', 'created_at'
        ]


class CollegeListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for college listings"""
    
    courses_count = serializers.SerializerMethodField()
    city_display = serializers.CharField(source='get_city_display', read_only=True)
    
    class Meta:
        model = College
        fields = [
            'id', 'name', 'slug', 'city', 'city_display', 'college_type',
            'short_description', 'logo', 'banner_image', 'overall_rating',
            'total_reviews', 'placement_percentage', 'average_package',
            'highest_package', 'nirf_rank', 'accreditation', 'is_featured',
            'courses_count', 'created_at'
        ]
    
    def get_courses_count(self, obj):
        return obj.courses.filter(is_active=True).count()


class CollegeDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single college view"""
    
    courses = CourseSerializer(many=True, read_only=True)
    city_display = serializers.CharField(source='get_city_display', read_only=True)
    type_display = serializers.CharField(source='get_college_type_display', read_only=True)
    recent_reviews = serializers.SerializerMethodField()
    
    class Meta:
        model = College
        fields = '__all__'
    
    def get_recent_reviews(self, obj):
        reviews = obj.reviews.filter(is_published=True)[:5]
        return CollegeReviewSerializer(reviews, many=True).data


class CollegeCompareSerializer(serializers.ModelSerializer):
    """Serializer for college comparison"""
    
    courses = CourseSerializer(many=True, read_only=True)
    city_display = serializers.CharField(source='get_city_display', read_only=True)
    
    class Meta:
        model = College
        fields = [
            'id', 'name', 'city', 'city_display', 'college_type', 'established_year',
            'affiliated_to', 'accreditation', 'nirf_rank', 'campus_area',
            'total_students', 'faculty_count', 'facilities', 'placement_percentage',
            'average_package', 'highest_package', 'top_recruiters', 'courses',
            'overall_rating', 'total_reviews', 'website', 'phone', 'email',
            'total_fees_range'
        ]
    
    total_fees_range = serializers.SerializerMethodField()
    
    def get_total_fees_range(self, obj):
        courses = obj.courses.filter(is_active=True)
        if courses.exists():
            return {
                'min': float(courses.order_by('total_fees').first().total_fees),
                'max': float(courses.order_by('-total_fees').first().total_fees)
            }
        return {'min': 0, 'max': 0}


class CollegeReviewSerializer(serializers.ModelSerializer):
    overall_rating = serializers.ReadOnlyField()
    college_name = serializers.CharField(source='college.name', read_only=True)
    
    class Meta:
        model = CollegeReview
        fields = [
            'id', 'college', 'college_name', 'reviewer_name', 'course_studied',
            'batch_year', 'academics_rating', 'infrastructure_rating',
            'placements_rating', 'faculty_rating', 'overall_rating',
            'title', 'review_text', 'is_verified', 'created_at'
        ]
        read_only_fields = ['id', 'is_verified', 'created_at']
    
    def validate(self, data):
        # Ensure ratings are between 1 and 5
        rating_fields = ['academics_rating', 'infrastructure_rating', 
                        'placements_rating', 'faculty_rating']
        for field in rating_fields:
            if field in data and not (1 <= data[field] <= 5):
                raise serializers.ValidationError(
                    {field: "Rating must be between 1 and 5"}
                )
        return data