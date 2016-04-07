from django.contrib.auth.models import User
from django.db import models

class Petition(models.Model):
    user = models.ForeignKey(User, default=1)
    title = models.CharField(max_length=100)
    content = models.TextField()
    category = models.CharField(max_length=20)
    is_archived = models.BooleanField(default=False)

    def __str__(self):
        return self.title