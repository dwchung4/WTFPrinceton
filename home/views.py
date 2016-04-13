from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from .forms import PetitionForm
from .models import Petition
from django.template.defaulttags import csrf_token
import psycopg2
import urlparse
import os
from website import database
from datetime import datetime, timedelta

def index(request, vote):
	if vote:
		conn = database.connect()
		cur = conn.cursor()
		cur.execute("UPDATE petition SET vote = vote+1 WHERE id = %s;", (vote,))
		conn.commit()
		return HttpResponseRedirect('../')

	petitions = []
	query = request.GET.get("q")
	if query:
		conn = database.connect()
		cur = conn.cursor()
		formattedquery = '%'+query+'%'
		cur.execute("SELECT DISTINCT * FROM petition WHERE (LOWER(title) LIKE LOWER(%s) \
			OR LOWER(content) LIKE LOWER(%s) OR LOWER(netid) LIKE LOWER(%s)) \
			AND is_archived = 'false' ORDER BY expiration;", (formattedquery, formattedquery, formattedquery,))
		for petition in cur.fetchall():
			now = datetime.now()
			timeleft = petition[6].replace(tzinfo=None)-now
			print timeleft
			days = timeleft.days
			if days == 0:
				hours = timeleft.total_seconds() // 3600
				petitionlist = list(petition)
				petitionlist.append(hours)
				petitionlist.append("hours")
				petition = tuple(petitionlist)
				petitions.append(petition)
			else:
				petitionlist = list(petition)
				petitionlist.append(days)
				petitionlist.append("days")
				petition = tuple(petitionlist)
				petitions.append(petition)
		if request.user.is_authenticated():
			return render(request, 'home/index.html', {
				'petitions': petitions,
				'netid': request.user,
			})
		else:
			return render(request, 'home/index_visitor.html', {
				'petitions': petitions,
			})
	else:
		conn = database.connect()
		cur = conn.cursor()
		cur.execute("SELECT * FROM petition ORDER BY expiration;")
		for petition in cur.fetchall():
			now = datetime.now()
			timeleft = petition[6].replace(tzinfo=None)-now
			print timeleft
			days = timeleft.days
			if days == 0:
				hours = timeleft.total_seconds() // 3600
				petitionlist = list(petition)
				petitionlist.append(hours)
				petitionlist.append("hours")
				petition = tuple(petitionlist)
				petitions.append(petition)
			else:
				petitionlist = list(petition)
				petitionlist.append(days)
				petitionlist.append("days")
				petition = tuple(petitionlist)
				petitions.append(petition)
		if request.user.is_authenticated():
			return render(request, 'home/index.html', {
				'netid': request.user,
				'petitions': petitions,
			})
		else:
			return render(request, 'home/index_visitor.html', {
				'petitions': petitions,
			})

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
			conn = database.connect()
			cur = conn.cursor()
			expiration = datetime.now()+timedelta(days=30)
			cur.execute("INSERT INTO petition(netid, title, content, category, is_archived, expiration, vote) \
				VALUES (%s, %s, %s, %s, %s, %s, %s)",
				(str(request.user), str(petition.title), str(petition.content), str(petition.category),
				'false', expiration, 0,))
			conn.commit()
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
		petitions = []
		conn = database.connect()
		cur = conn.cursor()
		cur.execute("SELECT * FROM petition WHERE netid = %s ORDER BY expiration", (str(netid),))
		for petition in cur.fetchall():
			now = datetime.now()
			timeleft = petition[6].replace(tzinfo=None)-now
			print timeleft
			days = timeleft.days
			if days == 0:
				hours = timeleft.total_seconds() // 3600
				petitionlist = list(petition)
				petitionlist.append(hours)
				petitionlist.append("hours")
				petition = tuple(petitionlist)
				petitions.append(petition)
			else:
				petitionlist = list(petition)
				petitionlist.append(days)
				petitionlist.append("days")
				petition = tuple(petitionlist)
				petitions.append(petition)
		return render(request, 'home/my_petitions.html', {
			'petitions': petitions,
			'netid': netid,
		})