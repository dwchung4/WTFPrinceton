from django.contrib.auth.models import User
from django.db import models
from datetime import datetime, timedelta

class Petition(models.Model):
	id = models.AutoField(primary_key=True)
	netid = models.ForeignKey(User)
	title = models.CharField(max_length=100)
	content = models.TextField()
	category = models.CharField(max_length=20)
	is_archived = models.BooleanField()
	expiration = models.DateTimeField()

	def __str__(self):
		return self.title

class Comment(models.Model):
	petition = models.ForeignKey(Petition)
	content = models.CharField(max_length=500)

	def __str__(self):
		return self.content