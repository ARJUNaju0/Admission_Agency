from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify

class College(models.Model):
    """Main College model with comprehensive details"""
    
    CITY_CHOICES = [
        ('mysore', 'Mysore'),
        ('bangalore', 'Bangalore'),
    ]
    
    TYPE_CHOICES = [
        ('government', 'Government'),
        ('private', 'Private'),
        ('deemed', 'Deemed University'),
    ]
    
    ACCREDITATION_CHOICES = [
        ('A++', 'A++'),
        ('A+', 'A+'),
        ('A', 'A'),
        ('B++', 'B++'),
        ('B+', 'B+'),
        ('B', 'B'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    established_year = models.IntegerField(validators=[MinValueValidator(1800)])
    college_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    
    # Location
    city = models.CharField(max_length=50, choices=CITY_CHOICES)
    address = models.TextField()
    pincode = models.CharField(max_length=10)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Contact Information
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField()
    
    # Academic Details
    affiliated_to = models.CharField(max_length=255)
    approved_by = models.CharField(max_length=255)  # AICTE, UGC, etc.
    accreditation = models.CharField(max_length=10, choices=ACCREDITATION_CHOICES, null=True, blank=True)
    naac_grade = models.CharField(max_length=10, blank=True)
    nirf_rank = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1)])
    
    # Infrastructure
    campus_area = models.DecimalField(max_digits=10, decimal_places=2, help_text="in acres")
    total_students = models.IntegerField(validators=[MinValueValidator(0)])
    faculty_count = models.IntegerField(validators=[MinValueValidator(0)])
    
    # Facilities (JSON stored as text in MongoDB)
    facilities = models.JSONField(default=list, help_text="List of available facilities")
    
    # Placements
    placement_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True,
        blank=True
    )
    average_package = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="in LPA")
    highest_package = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="in LPA")
    top_recruiters = models.JSONField(default=list, blank=True)
    
    # Media
    logo = models.ImageField(upload_to='colleges/logos/', null=True, blank=True)
    banner_image = models.ImageField(upload_to='colleges/banners/', null=True, blank=True)
    gallery_images = models.JSONField(default=list, blank=True)
    
    # Description
    description = models.TextField()
    short_description = models.CharField(max_length=500)
    
    # SEO
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Ratings
    overall_rating = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    total_reviews = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_featured', '-overall_rating', 'name']
        indexes = [
            models.Index(fields=['city', 'is_active']),
            models.Index(fields=['college_type']),
            models.Index(fields=['-overall_rating']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Course(models.Model):
    """Course offerings for colleges"""
    
    LEVEL_CHOICES = [
        ('ug', 'Undergraduate'),
        ('pg', 'Postgraduate'),
        ('diploma', 'Diploma'),
        ('certificate', 'Certificate'),
    ]
    
    STREAM_CHOICES = [
        ('engineering', 'Engineering'),
        ('medicine', 'Medicine'),
        ('commerce', 'Commerce'),
        ('science', 'Science'),
        ('arts', 'Arts'),
        ('management', 'Management'),
        ('law', 'Law'),
        ('pharmacy', 'Pharmacy'),
    ]
    
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='courses')
    
    # Course Details
    name = models.CharField(max_length=255)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    stream = models.CharField(max_length=50, choices=STREAM_CHOICES)
    duration_years = models.DecimalField(max_digits=3, decimal_places=1)
    
    # Fees
    total_fees = models.DecimalField(max_digits=10, decimal_places=2)
    per_year_fees = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Admission
    seats_available = models.IntegerField(validators=[MinValueValidator(0)])
    eligibility = models.TextField()
    entrance_exams = models.JSONField(default=list)  # ["JEE Main", "KCET"]
    
    # Details
    description = models.TextField()
    syllabus = models.TextField(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['college', 'level', 'name']
        unique_together = ['college', 'name', 'level']
    
    def __str__(self):
        return f"{self.name} - {self.college.name}"


class Facility(models.Model):
    """Facility/Infrastructure details"""
    
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class")
    description = models.TextField()
    
    class Meta:
        verbose_name_plural = "Facilities"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class CollegeReview(models.Model):
    """Student reviews for colleges"""
    
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='reviews')
    
    # Reviewer Info
    reviewer_name = models.CharField(max_length=100)
    reviewer_email = models.EmailField()
    course_studied = models.CharField(max_length=100)
    batch_year = models.IntegerField()
    
    # Ratings (1-5)
    academics_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    infrastructure_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    placements_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    faculty_rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    # Review
    title = models.CharField(max_length=200)
    review_text = models.TextField()
    
    # Verification
    is_verified = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review by {self.reviewer_name} for {self.college.name}"
    
    @property
    def overall_rating(self):
        """Calculate average rating"""
        return (
            self.academics_rating + 
            self.infrastructure_rating + 
            self.placements_rating + 
            self.faculty_rating
        ) / 4