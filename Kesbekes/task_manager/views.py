from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile, Task
from .forms import CustomUserCreationForm, UserProfileForm, TaskForm
from .ai_manager import analyze_task, get_ai_response
from django.contrib.auth.decorators import login_required
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
            # Log form errors for debugging
            print("User Creation Form Errors:", form.errors)
            print("User Profile Form Errors:", profile_form.errors)
            messages.error(request, 'Form is not valid. Please check the data and try again.')
            if User.objects.filter(username=request.POST.get('username')).exists():
                messages.error(request, 'Username already exists.')
            if User.objects.filter(email=request.POST.get('email')).exists():
                messages.error(request, 'Email already exists.')
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
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            task_details = analyze_task(task_description, current_time)
            if not task_details:
                messages.error(request, 'Failed to analyze task. Please try again.')
                return redirect('add_task')
            
            try:
                user_profile = UserProfile.objects.get(user=request.user)
            except UserProfile.DoesNotExist:
                messages.error(request, 'UserProfile does not exist. Please complete your profile.')
                return redirect('complete_profile')  # Redirect to a view where the user can complete their profile
            
            print(user_profile.wake_up_time)
            print(user_profile.objects.all())
            upcoming_tasks = Task.objects.filter(user=request.user, date__gte=datetime.today(), date__lte=datetime.today() + timedelta(days=7))
            ai_response = get_ai_response(task_details, user_profile, upcoming_tasks, current_time)

            messages.success(request, 'Task analyzed successfully.')
            return render(request, 'task_manager/task_analysis.html', {'task_details': task_details, 'ai_response': ai_response})
    else:
        form = TaskForm()
    return render(request, 'task_manager/add_task.html', {'form': form})

def complete_profile_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST)
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = request.user
            profile.save()
            messages.success(request, 'Profile completed successfully.')
            return redirect('home')
    else:
        profile_form = UserProfileForm()
    return render(request, 'task_manager/complete_profile.html', {'profile_form': profile_form})

@login_required
def confirm_task_view(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        date = request.POST['date']
        time = request.POST['time']
        priority = request.POST['priority']
        difficulty = request.POST['difficulty']

        Task.objects.create(
            user=request.user,
            title=title,
            description=description,
            date=date,
            time=time,
            priority=priority,
            difficulty=difficulty
        )

        messages.success(request, 'Task added successfully.')
        return redirect('home')
    return redirect('add_task')