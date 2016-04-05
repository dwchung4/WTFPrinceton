from django.contrib.auth.models import Permission, User
from django.db import models

# Create your models here.
class Greeting(models.Model):
	artist = models.CharField(max_length=250)

	def __str__(self):
		return self.artist