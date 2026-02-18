from django.db import models
from django.contrib.auth.models import User
from colleges.models import College, Course
from django.db.models.signals import post_save
from django.dispatch import receiver

class Inquiry(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('contacted', 'Contacted'),
        ('admitted', 'Admitted'),
        ('closed', 'Closed'),
    )

    # Student Details
    student_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    message = models.TextField(blank=True)

    # What are they interested in?
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='inquiries')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)

    # Agent Management
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Inquiries"

    def __str__(self):
        return f"{self.student_name} - {self.college.name}"

# --- Agent Customization ---
class AgentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent_profile')
    
    # Stores settings like: {"dark_mode": false, "show_stats": true, "compact_view": false}
    dashboard_config = models.JSONField(default=dict)

    def __str__(self):
        return f"Profile: {self.user.username}"

# Auto-create AgentProfile when a new User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        AgentProfile.objects.create(user=instance, dashboard_config={
            "show_stats": True,
            "show_recent": True,
            "compact_view": False
        })
