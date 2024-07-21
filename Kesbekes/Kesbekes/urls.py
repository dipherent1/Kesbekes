from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('calendar/', include('calendar_app.urls')),
    path('', include('task_manager.urls')),
]
