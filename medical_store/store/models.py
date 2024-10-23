from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Medicine(models.Model):
    id = models.BigAutoField(primary_key=True)  # Explicit primary key
    name = models.CharField(max_length=100)
    stock = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name
