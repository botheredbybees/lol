# ===============================
# gamification/models.py  
# ===============================
from django.contrib.auth.models import User
from django.db import models
from model_utils.models import TimeStampedModel

class Achievement(TimeStampedModel):
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='achievements/')
    points_value = models.IntegerField(default=10)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class UserAchievement(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'achievement']

class PointTransaction(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    points = models.IntegerField()
    description = models.CharField(max_length=200)
    transaction_type = models.CharField(max_length=20, choices=[
        ('earn', 'Earned'),
        ('spend', 'Spent'),
        ('bonus', 'Bonus'),
    ])
