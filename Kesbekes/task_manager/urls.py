from django.urls import path
from .views import signup_view, login_view, logout_view, home_view, add_task_view, confirm_task_view

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('', home_view, name='home'),
    path('add_task/', add_task_view, name='add_task'),
    path('confirm_task/', confirm_task_view, name='confirm_task'),
]
