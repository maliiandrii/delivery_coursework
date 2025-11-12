from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm


def register_view(request):
    """
    Handle user registration.
    Creates new user account and automatically logs them in.
    """
    if request.user.is_authenticated:
        return redirect('product_list')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')

            if user.is_courier():
                return redirect('courier_orders')
            return redirect('product_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """
    Handle user login.
    Redirects couriers to courier dashboard, customers to product list.
    """
    if request.user.is_authenticated:
        return redirect('product_list')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')

                if user.is_courier():
                    return redirect('courier_orders')
                if user.is_superuser:
                    return redirect('admin:index')
                return redirect('product_list')
            else:
                messages.error(request, 'Invalid credentials')
        else:
            messages.error(request, 'Invalid credentials')
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def profile_view(request):
    """
    Display and update user profile.
    Shows order history and allows profile editing.
    """

    if request.user.is_superuser:
        return redirect('admin:index')

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserProfileForm(instance=request.user)

    return render(request, 'accounts/profile.html', {
        'form': form,
        'user': request.user
    })
