from django.contrib.auth.models import User
from django.db import models
from datetime import datetime, timedelta

class Petition(models.Model):
	categories = (
		('Academics', 'Academics'),
		('Athletics & Recreation', 'Athletics & Recreation'),
		('Community Issues', 'Community Issues'),
		('Dining', 'Dining'),
		('Housing & Facilities', 'Housing & Facilities'),
		('Student Activities', 'Student Activities'),
		('Student Services', 'Student Services'),
		('Other', 'Other')
	)

	id = models.AutoField(primary_key=True)
	netid = models.ForeignKey(User)
	title = models.CharField(max_length=100)
	content = models.CharField(max_length=500)
	category = models.CharField(max_length=30, choices=categories)
	is_archived = models.BooleanField()
	expiration = models.DateTimeField()
	vote = models.IntegerField()

	def __str__(self):
		return self.title

class Comment(models.Model):
	petition = models.ForeignKey(Petition)
	content = models.CharField(max_length=500)

	def __str__(self):
		return self.content