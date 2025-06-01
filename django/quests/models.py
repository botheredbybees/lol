# ===============================
# quests/models.py
# ===============================
from django.contrib.auth.models import User
from django.db import models
from model_utils.models import TimeStampedModel

class Quest(TimeStampedModel):
    title = models.CharField(max_length=200)
    description = models.TextField()
    story_prompt = models.TextField()  # For AI generation
    background_image = models.ImageField(upload_to='quest_backgrounds/', null=True, blank=True)
    difficulty = models.IntegerField(choices=[
        (1, 'Easy'),
        (2, 'Medium'),
        (3, 'Hard'),
        (4, 'Epic')
    ])
    points_reward = models.IntegerField(default=50)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title

class QuestProgress(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ], default='not_started')
    progress_data = models.JSONField(default=dict)  # Store quest-specific progress
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'quest']