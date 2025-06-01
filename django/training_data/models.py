# ===============================
# training_data/models.py
# ===============================
from django.db import models
from model_utils.models import TimeStampedModel
import json

class TrainingPackage(TimeStampedModel):
    name = models.CharField(max_length=200)
    description = models.TextField()
    difficulty_level = models.IntegerField(choices=[
        (1, 'Beginner'),
        (2, 'Intermediate'), 
        (3, 'Advanced'),
        (4, 'Expert')
    ])
    estimated_duration = models.DurationField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class TrainingUnit(TimeStampedModel):
    package = models.ForeignKey(TrainingPackage, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    content = models.TextField()
    order = models.IntegerField()
    points_value = models.IntegerField(default=10)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.package.name} - {self.name}"