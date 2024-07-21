from django.urls import path
from .views import calendar_view, day_tasks_view

urlpatterns = [
    path('', calendar_view, name='calendar'),
    path('<int:year>/<int:month>/<int:day>/', day_tasks_view, name='day_tasks'),
]
