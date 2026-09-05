"""
Custom admin views for admin panel
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View


def custom_admin_login(request):
    """
    Custom login view for admin panel
    """
    if request.user.is_authenticated:
        return redirect('/admin-panel/')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    next_url = request.GET.get('next', '/admin-panel/')
                    return redirect(next_url)
                else:
                    messages.error(request, 'Akun tidak aktif.')
            else:
                messages.error(request, 'Username atau password salah.')
        else:
            messages.error(request, 'Username dan password harus diisi.')
    
    return render(request, 'admin_panel/login.html')


@login_required
def custom_admin_logout(request):
    """
    Custom logout view for admin panel
    """
    logout(request)
    messages.success(request, 'Anda telah berhasil logout.')
    return redirect('/admin-panel/login/')


@login_required
def admin_dashboard(request):
    """
    Admin dashboard view
    """
    context = {
        'user': request.user,
        'page_title': 'Dashboard Admin Panel',
    }
    return render(request, 'admin_panel/dashboard.html', context)
