from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile, Task
from .forms import CustomUserCreationForm, UserProfileForm, TaskForm
from .ai_manager import analyze_task, get_ai_response
from datetime import datetime
from datetime import datetime, timedelta
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if form.is_valid() and profile_form.is_valid():
            user = form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, 'Account created successfully. Please login.')
            return redirect('login')
        else:
            messages.error(request, 'Form is not valid. Please check the data and try again.')
            if User.objects.filter(username=request.POST.get('username')).exists():
                messages.error(request, 'Username already exists.')
            if User.objects.filter(email=request.POST.get('email')).exists():
                messages.error(request, 'Email already exists.')
            print("Form errors:", form.errors)
            print("Profile form errors:", profile_form.errors)
    else:
        form = CustomUserCreationForm()
        profile_form = UserProfileForm()
    return render(request, 'task_manager/signup.html', {'form': form, 'profile_form': profile_form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Logged in successfully.')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'task_manager/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('login')

def home_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    tasks = Task.objects.filter(user=request.user, date=datetime.today())
    return render(request, 'task_manager/home.html', {'tasks': tasks})

def add_task_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task_description = form.cleaned_data['description']
            task_details = analyze_task(task_description)
            user_profile = UserProfile.objects.get(user=request.user)
            upcoming_tasks = Task.objects.filter(user=request.user, date__gte=datetime.today(), date__lte=datetime.today() + timedelta(days=7))
            ai_response = get_ai_response(task_details, user_profile, upcoming_tasks)

            messages.success(request, 'Task analyzed successfully.')
            return render(request, 'task_manager/task_analysis.html', {'task_details': task_details, 'ai_response': ai_response})
    else:
        form = TaskForm()
    return render(request, 'task_manager/add_task.html', {'form': form})
