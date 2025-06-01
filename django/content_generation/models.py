# ===============================
# content_generation/models.py
# ===============================
from django.db import models
from model_utils.models import TimeStampedModel

class GeneratedContent(TimeStampedModel):
    content_type = models.CharField(max_length=50, choices=[
        ('quest_background', 'Quest Background'),
        ('card_art', 'Card Art'),
        ('character_portrait', 'Character Portrait'),
        ('story_text', 'Story Text')
    ])
    prompt = models.TextField()
    generated_text = models.TextField(blank=True)
    generated_image = models.ImageField(upload_to='generated/', null=True, blank=True)
    generation_parameters = models.JSONField(default=dict)
    is_approved = models.BooleanField(default=False)
    related_object_id = models.IntegerField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"{self.content_type} - {self.created.strftime('%Y-%m-%d')}"