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
from website import database
from datetime import datetime, timedelta

def index(request):
	if request.user.is_authenticated():
		return render(request, 'home/index.html', {
			'netid': request.user,
		})
	else:
		return render(request, 'home/index_visitor.html')

def about(request):
	if request.user.is_authenticated():
		return render(request, 'home/about.html', {
			'netid': request.user,
		})
	else:
		return render(request, 'home/about_visitor.html')

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
				conn = database.connect()
			except:
				print "unable to connect to the datbase"
			cur = conn.cursor()
			try:
				cur.execute("INSERT INTO petition(netid, title, content, category, is_archived, expiration) VALUES (%s, %s, %s, %s, %s, %s)", (str(request.user), str(petition.title), str(petition.content), str(petition.category), 'false', datetime.now()+timedelta(days=30),))
				conn.commit()
			except:
				print "failed to insert"
			return HttpResponseRedirect('../')
		context = {
			"form": form,
			"netid": request.user,
		}
		return render(request, 'home/create_petition.html', context)

def my_petitions(request, netid):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('../login/')
	else:
		try:
			petitions = []
			try:
				conn = database.connect()
			except:
				print "unable to connect to the database"
			cur = conn.cursor()
			try:
				cur.execute("SELECT * FROM petition WHERE netid = %s", (str(netid),))
				for petition in cur.fetchall():
					petitions.append(petition)
			except:
				print "failed to get petitions"
		except Petition.DoesNotExist:
			petitions = []
		return render(request, 'home/my_petitions.html', {
			'petitions': petitions,
			'netid': request.user,
		})