from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from .forms import PetitionForm
from .models import Petition
import psycopg2
import os
from website import database
from datetime import datetime, timedelta


def index(request):

	orderList = ['Recent', 'Top']
	statusList = ['Active', 'Expired', 'Pending', 'Completed']
	categoryList = ['All', 'Academics', 'Athletics & Recreation', 'Community Issues', 'Dining', 
		'Housing & Facilities', 'Student Activities', 'Student Services', 'Other']

	order = request.GET.get("order")
	if order == None:
		order = 'Recent'
	status = request.GET.get("status")
	if status == None:
		status = 'Active'
	category = request.GET.get("category")
	if category == None:
		category = 'All'

	# move current filter to the front of list
	orderList.remove(order)
	orderList.insert(0, order)
	statusList.remove(status)
	statusList.insert(0, status)
	categoryList.remove(category)
	categoryList.insert(0, category)

	petitions = []
	conn = database.connect()
	cur = conn.cursor()

	# search query
	query = request.GET.get("q")
	if query:
		formattedquery = '%'+query+'%'
		cur.execute("SELECT DISTINCT * FROM petition WHERE LOWER(title) LIKE LOWER(%s) \
			OR LOWER(content) LIKE LOWER(%s) OR LOWER(netid) LIKE LOWER(%s) \
			ORDER BY expiration DESC;", (formattedquery, formattedquery, formattedquery,))
	else:
		if category == None or category == 'All':
			if order == None or order == 'Recent':
				cur.execute("SELECT * FROM petition WHERE status = %s ORDER BY expiration;", (status,))
			else:
				cur.execute("SELECT * FROM petition WHERE status = %s ORDER BY vote DESC, expiration;", (status,))
		else:
			if order == None or order == 'Recent':
				cur.execute("SELECT * FROM petition WHERE status = %s AND category = %s ORDER BY expiration;", 
					(status, category,))
			else:
				cur.execute("SELECT * FROM petition WHERE status = %s AND category = %s ORDER BY vote DESC, expiration;", 
					(status, category,))

	for petition in cur.fetchall():
		petition = addRemainingTime(petition)
		# if expired, change status to 'Expired'
		if petition[10] < 0 and petition[7] == 'Active':
			conn1 = database.connect()
			cur1 = conn1.cursor()
			cur1.execute("UPDATE petition SET status = 'Expired' WHERE id = %s;", (petition[0],))
			conn1.commit()
			tempList = list(petition)
			tempList[7] = 'Expired'
			petition = tuple(tempList)

		# add filtered petitions to list
		if query:
			petitions.append(petition)
		elif petition[7] == status:
			petitions.append(petition)

	if request.user.is_authenticated():
		return render(request, 'home/index.html', {
			'netid': str(request.user),
			'petitions': petitions,
			'orderList': orderList,
			'statusList': statusList,
			'categoryList': categoryList,
		})
	else:
		return render(request, 'home/index_visitor.html', {
			'petitions': petitions,
			'orderList': orderList,
			'statusList': statusList,
			'categoryList': categoryList,
		})


def about(request):
	if request.user.is_authenticated():
		return render(request, 'home/about.html', {
			'netid': str(request.user),
		})
	else:
		return render(request, 'home/about_visitor.html')


def create_petition(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('../login/create_petition')
	else:
		form = PetitionForm(request.POST or None)
		if form.is_valid():
			petition = form.save(commit=False)
			context = {
				'petition': petition,
			}
			conn = database.connect()
			cur = conn.cursor()
			expiration = datetime.now()+timedelta(minutes=2)
			cur.execute("INSERT INTO petition(netid, title, content, category, status, expiration, vote) \
				VALUES (%s, %s, %s, %s, %s, %s, %s)",
				(str(request.user), str(petition.title), str(petition.content), str(petition.category),
				'Active', expiration, 0,))
			conn.commit()
			return HttpResponseRedirect('../')
		context = {
			"form": form,
			"netid": str(request.user),
		}
		return render(request, 'home/create_petition.html', context)


def add_comment(request, id):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('../login/')
	else:
		query = request.GET.get("r")
		if query:
			conn = database.connect()
			cur = conn.cursor()
			formattedquery = '{'+query+'}'
			cur.execute("UPDATE petition SET comments = comments || %s WHERE id = %s;", (formattedquery, str(id),))
			conn.commit()
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
		petitions = []
		conn = database.connect()
		cur = conn.cursor()
		#cur.execute("UPDATE petition SET comments = comments || '{%s}' WHERE id = %s;", (str(comment.content), str(id),))
		#conn.commit()
		cur.execute("SELECT * FROM petition ORDER BY expiration;")
		#return HttpResponseRedirect('../')
		for petition in cur.fetchall():
			petitions.append(petition)
		context = {
			'netid': request.user,
			'petitions': petitions,
		}
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def my_petitions(request, netid):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('../login/'+str(netid))
	else:
		query = request.GET.get("r")
		if query:
			conn = database.connect()
			cur = conn.cursor()
			formattedquery = '{'+query+'}'
			cur.execute("UPDATE petition SET comments = comments || %s WHERE id = %s;", (formattedquery, str(id),))
			conn.commit()
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
		petitions = []
		conn = database.connect()
		cur = conn.cursor()
		cur.execute("SELECT * FROM petition WHERE netid = %s ORDER BY expiration DESC", (str(netid),))
		for petition in cur.fetchall():
			petition = addRemainingTime(petition)
			if petition[9] < 0 and petition[7] == 'Active':
				conn1 = database.connect()
				cur1 = conn1.cursor()
				cur1.execute("UPDATE petition SET status = 'Expired' WHERE id = %s;", (petition[0],))
				conn1.commit()
				tempList = list(petition)
				tempList[7] = 'Expired'
				petition = tuple(tempList)
			petitions.append(petition)
		return render(request, 'home/my_petitions.html', {
			'petitions': petitions,
			'netid': str(netid),
			'user': str(request.user),
		})


def addRemainingTime(petition):
	now = datetime.now()
	timeleft = petition[5].replace(tzinfo=None)-now
	days = timeleft.days
	if days == 0:
		hours = timeleft.total_seconds()//3600
		if hours == 0:
			minutes = (timeleft.total_seconds()%3600)//60
			petitionlist = list(petition)
			petitionlist.append(int(minutes))
			petitionlist.append("minutes")
			petition = tuple(petitionlist)
		else:
			petitionlist = list(petition)
			petitionlist.append(int(hours))
			petitionlist.append("hours")
			petition = tuple(petitionlist)
	else:
		petitionlist = list(petition)
		petitionlist.append(int(days))
		petitionlist.append("days")
		petition = tuple(petitionlist)
	return petition


def delete_petition(request, petitionid):
	if request.META.get('HTTP_REFERER') == None:
		return HttpResponseRedirect('../')
	conn = database.connect()
	cur = conn.cursor()
	cur.execute("SELECT netid FROM petition WHERE id = %s", (petitionid,))
	if cur.rowcount != 0:
		id = cur.fetchone()[0]
		if str(id) == str(request.user):
			cur.execute("DELETE FROM petition WHERE id = %s", (petitionid,))
			conn.commit()
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def vote(request, petitionid, netid):
	if request.META.get('HTTP_REFERER') == None:
		return HttpResponseRedirect('../../')

	userid = request.user
	conn = database.connect()
	cur = conn.cursor()
	cur.execute("SELECT netid FROM petition WHERE id = %s;", (petitionid,))
	netid = cur.fetchone()[0]
	if (str(userid) == netid):
		return HttpResponseRedirect('../../')

	cur.execute("SELECT voteid FROM petition WHERE id = %s;", (petitionid,))
	voteid = cur.fetchone()
	for listid in voteid:
		if listid != None and str(userid) in listid:
			return HttpResponseRedirect('../../')

	cur.execute("SELECT vote FROM petition WHERE id = %s;", (petitionid,))
	vote = cur.fetchone()[0]
	now = datetime.now()
	cur.execute("SELECT expiration FROM petition WHERE id = %s;", (petitionid,))
	timeleft = cur.fetchone()[0].replace(tzinfo=None)-now


	if vote < 10 and timeleft.days >= 0:
		formattedid = '{'+str(userid)+'}'
		cur.execute("UPDATE petition SET vote = vote+1, voteid = voteid || %s WHERE id = %s;", (formattedid, petitionid,))
		conn.commit()
		vote += 1

		if vote == 10:
			cur.execute("UPDATE petition SET status = 'Pending' WHERE id = %s;", (petitionid,))
			conn.commit()

	if netid:
		return HttpResponseRedirect('../../my_petitions/'+netid)
	else:
		return HttpResponseRedirect('../../')


def howtouse(request):
	if request.user.is_authenticated():
		return render(request, 'home/howtouse.html', {
			'netid': request.user,
		})
	else:
		return render(request, 'home/howtouse_visitor.html')