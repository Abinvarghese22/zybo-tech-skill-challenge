"""
Views for user authentication: Register, Login, Logout.
All business logic is handled here (not in templates).
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.utils import timezone
from .forms import UserRegistrationForm, UserLoginForm


def register_view(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect('chat:user_list')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Welcome, {user.username}! Your account has been created.')
            return redirect('chat:user_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('chat:user_list')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            user.is_online = True
            user.save(update_fields=['is_online'])
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('chat:user_list')
        else:
            messages.error(request, 'Invalid email or password.')
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Handle user logout and update online status."""
    if request.user.is_authenticated:
        request.user.is_online = False
        request.user.last_seen = timezone.now()
        request.user.save(update_fields=['is_online', 'last_seen'])
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')
