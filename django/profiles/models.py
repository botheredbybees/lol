# ===============================
# profiles/models.py
# ===============================
from django.contrib.auth.models import User
from django.db import models
from model_utils.models import TimeStampedModel

class UserProfile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    level = models.IntegerField(default=1)
    experience_points = models.IntegerField(default=0)
    total_points = models.IntegerField(default=0)
    avatar_image = models.ImageField(upload_to='avatars/', null=True, blank=True)
    character_name = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - Level {self.level}"