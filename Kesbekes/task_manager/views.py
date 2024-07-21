from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile, Task
from .forms import CustomUserCreationForm, UserProfileForm, TaskForm
from .ai_manager import analyze_task, get_ai_response
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta

# View for user signup
def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if form.is_valid() and profile_form.is_valid():
            user = form.save()  # Save the user
            profile = profile_form.save(commit=False)
            profile.user = user  # Associate profile with the user
            profile.save()  # Save the user profile
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

# View for user login
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)  # Authenticate the user
        if user is not None:
            login(request, user)  # Log the user in
            messages.success(request, 'Logged in successfully.')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'task_manager/login.html')

# View for user logout
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('login')

# Home view to display tasks for the current day
def home_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    tasks = Task.objects.filter(user=request.user, date=datetime.today())  # Get tasks for today
    return render(request, 'task_manager/home.html', {'tasks': tasks})

# View to add a new task
def add_task_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task_description = form.cleaned_data['description']
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            task_details = analyze_task(task_description, current_time)  # Analyze task details using AI
            if not task_details:
                messages.error(request, 'Failed to analyze task. Please try again.')
                return redirect('add_task')
            
            try:
                user_profile = UserProfile.objects.get(user=request.user)  # Get user profile
            except UserProfile.DoesNotExist:
                messages.error(request, 'UserProfile does not exist. Please complete your profile.')
                return redirect('complete_profile')  # Redirect to profile completion view
            
            print(user_profile.wake_up_time)
            print(UserProfile.objects.all())
            upcoming_tasks = Task.objects.filter(
                user=request.user, 
                date__gte=datetime.today(), 
                date__lte=datetime.today() + timedelta(days=7)
            )  # Get upcoming tasks for the next 7 days
            ai_response = get_ai_response(task_details, user_profile, upcoming_tasks, current_time)  # Get AI response

            messages.success(request, 'Task analyzed successfully.')
            return render(request, 'task_manager/task_analysis.html', {'task_details': task_details, 'ai_response': ai_response})
    else:
        form = TaskForm()
    return render(request, 'task_manager/add_task.html', {'form': form})

# View to complete the user profile
def complete_profile_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST)
        if profile_form.is_valid():
            profile = profile_form.save(commit=False)
            profile.user = request.user  # Associate profile with the user
            profile.save()  # Save the user profile
            messages.success(request, 'Profile completed successfully.')
            return redirect('home')
    else:
        profile_form = UserProfileForm()
    return render(request, 'task_manager/complete_profile.html', {'profile_form': profile_form})

# View to confirm and save a new task
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
        )  # Create and save the new task

        messages.success(request, 'Task added successfully.')
        return redirect('home')
    return redirect('add_task')
