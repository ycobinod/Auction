from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass

class Listing(models.Model):
    name = models.CharField(max_length=64)
    starting_bid = models.IntegerField()
    description = models.CharField(max_length=254)
    category = models.CharField(max_length=64, blank=True)
    url = models.CharField(max_length=254)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner')
    active = models.BooleanField(default=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='winner', null=True, blank=True)

    def __str__(self):
        return f"{self.name} {self.starting_bid}$ {self.owner}"  