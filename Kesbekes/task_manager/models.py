from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    wake_up_time = models.CharField(max_length=255)
    sleep_time = models.CharField(max_length=255)
    productive_hours = models.CharField(max_length=255)
    preferred_categories = models.CharField(max_length=255)
    # study_duration = models.IntegerField()  # in minutes
    # study_environment = models.CharField(max_length=255)
    # major = models.CharField(max_length=255)
    # year_of_study = models.CharField(max_length=50)
    # recurring_commitments = models.TextField()
    # learning_style = models.CharField(max_length=255)
    # short_term_goals = models.TextField()
    # long_term_goals = models.TextField()

class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    priority = models.CharField(max_length=50)
    difficulty = models.CharField(max_length=50)

    def __str__(self):
        return self.title
