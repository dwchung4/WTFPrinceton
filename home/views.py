from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .forms import PetitionForm
from .models import Petition
from django.template.defaulttags import csrf_token
import psycopg2
import urlparse
import os

def index(request):
	return render(request, 'home/index.html')

def about(request):
	return render(request, 'home/about.html')

def contact(request):
	return render(request, 'home/contact.html')

def create_petition(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('../login/')
	else:
		form = PetitionForm(request.POST or None)
		if form.is_valid():
			petition = form.save(commit=False)
			context = {
				'petition': petition,
			}
			try:
				# On Heroku
				urlparse.uses_netloc.append("postgres")
				url = urlparse.urlparse(os.environ["DATABASE_URL"])
				conn = psycopg2.connect(
				    database=url.path[1:],
				    user=url.username,
				    password=url.password,
				    host=url.hostname,
				    port=url.port,
				)
				# local
				"""
				conn = psycopg2.connect(
				    database='d8qajk44a19ere',
				    user='',
				    password='',
				    host='localhost',
				    port='',
				)
				"""
			except:
				print "unable to connect to the datbase"
			cur = conn.cursor()
			try:
				cur.execute("INSERT INTO petition(netid, title, content, category, is_archived) VALUES (%s, %s, %s, %s, %s)", (str(request.user), str(petition.title), str(petition.content), str(petition.category), 'false',))
				conn.commit()
			except:
				print "failed to insert"

			return render(request, 'home/index.html')
		context = {
			"form": form,
		}
		return render(request, 'home/create_petition.html', context)

def my_petitions(request, netid):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('../login/')
	else:
		try:
			petitions = []
			try:
				# On Heroku
				urlparse.uses_netloc.append("postgres")
				url = urlparse.urlparse(os.environ["DATABASE_URL"])
				conn = psycopg2.connect(
				    database=url.path[1:],
				    user=url.username,
				    password=url.password,
				    host=url.hostname,
				    port=url.port,
				)
				# local
				"""
				conn = psycopg2.connect(
				    database='d8qajk44a19ere',
				    user='',
				    password='',
				    host='localhost',
				    port='',
				)
				"""
			except:
				print "unable to connect to the database"
			cur = conn.cursor()
			try:
				cur.execute("SELECT * FROM petition WHERE netid = %s", (str(netid),))
				for petition in cur.fetchall():
					print petition
					petitions.append(petition)
			except:
				print "failed to get petitions"
		except Petition.DoesNotExist:
			petitions = []
		return render(request, 'home/my_petitions.html', {
			'petitions': petitions,
		})