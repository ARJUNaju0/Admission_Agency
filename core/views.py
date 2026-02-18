from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

from colleges.models import College
from agency.models import Inquiry

def home(request):
    context = {
        'total_colleges': College.objects.filter(is_active=True).count(),
        'total_inquiries': Inquiry.objects.count(),
    }
    return render(request, 'core/home.html', context)

def admin_login_view(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Try to find user by email
        try:
            user = User.objects.get(email=email)
            username = user.username
        except User.DoesNotExist:
            messages.error(request, 'Invalid email or password')
            return render(request, 'registration/admin_login.html')
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Welcome back to the admin portal!')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid email or password')
    
    return render(request, 'registration/admin_login.html')

@login_required
def admin_logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully')
    return redirect('admin_login')