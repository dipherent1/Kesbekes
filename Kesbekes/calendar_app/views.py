from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta, date
from task_manager.models import Task

# Function to get the current month's calendar days
def get_month_calendar(year, month):
    import calendar
    cal = calendar.Calendar()
    return cal.itermonthdays(year, month)

# View to show the calendar
def calendar_view(request):
    today = timezone.now()
    year = today.year
    month = today.month
    month_days = get_month_calendar(year, month)
    tasks = Task.objects.filter(user=request.user, date__month=month, date__year=year)
    
    # Dictionary to hold tasks for each day
    tasks_by_day = {}
    for task in tasks:
        day = task.date.day
        if day not in tasks_by_day:
            tasks_by_day[day] = []
        tasks_by_day[day].append(task)
    
    return render(request, 'calendar_app/calendar.html', {
        'month_days': month_days,
        'tasks_by_day': tasks_by_day,
        'year': year,
        'month': month
    })

# View to show tasks for a specific day
def day_tasks_view(request, year, month, day):
    tasks = Task.objects.filter(user=request.user, date=date(year, month, day))
    return render(request, 'calendar_app/day_tasks.html', {'tasks': tasks, 'day': day, 'month': month, 'year': year})
