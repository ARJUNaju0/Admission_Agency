from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from .models import Inquiry, AgentProfile
from .forms import InquiryForm, InquiryResponseForm
from colleges.models import College

def create_inquiry(request, college_id):
    college = get_object_or_404(College, id=college_id)
    
    if request.method == 'POST':
        form = InquiryForm(request.POST, college_id=college_id)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.college = college
            inquiry.save()
            
            # If it's an AJAX request (from Modal), return JSON
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': 'Inquiry sent successfully!'})
            
            messages.success(request, "Your inquiry has been sent! An agent will contact you soon.")
            return redirect('college_detail', pk=college_id)
    
    return redirect('college_detail', pk=college_id)

@login_required
def agent_dashboard(request):
    profile, created = AgentProfile.objects.get_or_create(user=request.user)
    
    # Handle Dashboard Customization (Toggle Widgets)
    if request.method == "POST" and 'update_config' in request.POST:
        config = profile.dashboard_config
        
        # Toggle boolean values based on checkbox presence
        config['show_stats'] = 'show_stats' in request.POST
        config['show_recent'] = 'show_recent' in request.POST
        config['compact_view'] = 'compact_view' in request.POST
        
        profile.dashboard_config = config
        profile.save()
        messages.success(request, "Dashboard layout updated.")
        return redirect('admin_dashboard')

    # Handle Status Updates (e.g., moving an inquiry from Pending -> Contacted)
    if request.method == "POST" and 'update_status' in request.POST:
        inquiry_id = request.POST.get('inquiry_id')
        new_status = request.POST.get('status')
        inquiry = get_object_or_404(Inquiry, id=inquiry_id)
        inquiry.status = new_status
        inquiry.save()
        messages.success(request, f"Inquiry status updated to {new_status}")
        return redirect('admin_dashboard')

    # Handle Email Response
    if request.method == "POST" and 'send_email' in request.POST:
        inquiry_id = request.POST.get('inquiry_id')
        inquiry = get_object_or_404(Inquiry, id=inquiry_id)
        
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [inquiry.email],
                fail_silently=False,
            )
            messages.success(request, f"Email sent successfully to {inquiry.student_name}")
            inquiry.status = 'contacted'
            inquiry.save()
        except Exception as e:
            messages.error(request, f"Failed to send email: {str(e)}")
        
        return redirect('admin_dashboard')

    # Data for the Template
    context = {
        'inquiries': Inquiry.objects.all().order_by('-created_at'),
        'total_inquiries': Inquiry.objects.count(),
        'pending_count': Inquiry.objects.filter(status='pending').count(),
        'contacted_count': Inquiry.objects.filter(status='contacted').count(),
        'admitted_count': Inquiry.objects.filter(status='admitted').count(),
        'closed_count': Inquiry.objects.filter(status='closed').count(),
        'config': profile.dashboard_config,
        'recent_inquiries': Inquiry.objects.all()[:5],
        'stats': {
            'total': Inquiry.objects.count(),
            'pending': Inquiry.objects.filter(status='pending').count(),
            'contacted': Inquiry.objects.filter(status='contacted').count(),
            'conversion_rate': round(
                (Inquiry.objects.filter(status='admitted').count() / Inquiry.objects.count() * 100) 
                if Inquiry.objects.count() > 0 else 0, 1
            )
        }
    }
    return render(request, 'agency/dashboard.html', context)

@login_required
def inquiry_detail(request, inquiry_id):
    inquiry = get_object_or_404(Inquiry, id=inquiry_id)
    
    if request.method == 'POST':
        if 'send_email' in request.POST:
            subject = request.POST.get('subject')
            message = request.POST.get('message')
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [inquiry.email],
                    fail_silently=False,
                )
                messages.success(request, f"Email sent successfully to {inquiry.student_name}")
                inquiry.status = 'contacted'
                inquiry.save()
            except Exception as e:
                messages.error(request, f"Failed to send email: {str(e)}")
        
        elif 'update_status' in request.POST:
            new_status = request.POST.get('status')
            inquiry.status = new_status
            inquiry.save()
            messages.success(request, f"Inquiry status updated to {new_status}")
        
        return redirect('inquiry_detail', inquiry_id=inquiry_id)
    
    context = {
        'inquiry': inquiry,
        'email_form': InquiryResponseForm(initial={
            'subject': f'Re: Your inquiry about {inquiry.college.name}',
            'message': f'''Dear {inquiry.student_name},

Thank you for your interest in {inquiry.college.name}. We have received your inquiry and would be happy to assist you.

{inquiry.message if inquiry.message else 'Please let us know if you have any specific questions about the college or courses.'}

Best regards,
Aju Agency Team
Phone: {request.user.agent_profile.phone if hasattr(request.user, 'agent_profile') else 'Contact us for details'}
Email: {settings.DEFAULT_FROM_EMAIL}'''
        })
    }
    return render(request, 'agency/inquiry_detail.html', context)