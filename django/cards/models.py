# ===============================
# cards/models.py
# ===============================
from django.contrib.auth.models import User
from django.db import models
from model_utils.models import TimeStampedModel

class Card(TimeStampedModel):
    name = models.CharField(max_length=100)
    description = models.TextField()
    card_image = models.ImageField(upload_to='cards/', null=True, blank=True)
    attack_power = models.IntegerField(default=1)
    defense_power = models.IntegerField(default=1)
    rarity = models.CharField(max_length=20, choices=[
        ('common', 'Common'),
        ('uncommon', 'Uncommon'),
        ('rare', 'Rare'),
        ('epic', 'Epic'),
        ('legendary', 'Legendary')
    ])
    card_type = models.CharField(max_length=30)
    
    def __str__(self):
        return f"{self.name} ({self.rarity})"

class UserCard(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    
    class Meta:
        unique_together = ['user', 'card']