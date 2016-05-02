import psycopg2
import os
from website import database
from datetime import datetime, timedelta

from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from .forms import PetitionForm
from .models import Petition
import psycopg2
import os
from website import database
from datetime import datetime, timedelta
from django.contrib import messages
from django.conf import settings


def index(request):
	orderList = ['Recent', 'Top']
	statusList = ['All', 'Active', 'Expired', 'Pending', 'Completed']
	categoryList = ['All', 'Academics', 'Athletics & Recreation', 'Community Issues', 'Dining', 
		'Housing & Facilities', 'Student Activities', 'Student Services', 'Other']

	order = request.GET.get("order")
	if order == None:
		order = 'Recent'
	status = request.GET.get("status")
	if status == None:
		status = 'All'
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
		if query.isdigit():
			formattedquery = '%'+query+'%'
			cur.execute("SELECT DISTINCT * FROM petition WHERE LOWER(title) LIKE LOWER(%s) \
				OR LOWER(content) LIKE LOWER(%s) OR LOWER(netid) LIKE LOWER(%s) OR id = %s \
				ORDER BY expiration DESC;", (formattedquery, formattedquery, formattedquery, query,))
		else:
			formattedquery = '%'+query+'%'
			cur.execute("SELECT DISTINCT * FROM petition WHERE LOWER(title) LIKE LOWER(%s) \
				OR LOWER(content) LIKE LOWER(%s) OR LOWER(netid) LIKE LOWER(%s) \
				ORDER BY expiration DESC;", (formattedquery, formattedquery, formattedquery,))
	else:
		if category == 'All':
			if order == 'Recent':
				if status == 'All':
					cur.execute("SELECT * FROM petition ORDER BY expiration DESC;")
				else:
					cur.execute("SELECT * FROM petition WHERE status = %s ORDER BY expiration DESC;", (status,))
			else:
				if status == 'All':
					cur.execute("SELECT * FROM petition ORDER BY vote DESC, expiration DESC;")
				else:
					cur.execute("SELECT * FROM petition WHERE status = %s ORDER BY vote DESC, expiration DESC;", (status,))
		else:
			if order == 'Recent':
				if status == 'All':
					cur.execute("SELECT * FROM petition WHERE category = %s ORDER BY expiration DESC;", (category,))
				else:
					cur.execute("SELECT * FROM petition WHERE status = %s AND category = %s ORDER BY expiration DESC;", 
						(status, category,))
			else:
				if status == 'All':
					cur.execute("SELECT * FROM petition WHERE category = %s ORDER BY vote DESC, expiration DESC;", (status, category,))
				else:
					cur.execute("SELECT * FROM petition WHERE status = %s AND category = %s ORDER BY vote DESC, expiration DESC;", 
						(status, category,))

	for petition in cur.fetchall():
		petition = addRemainingTime(petition)
		# if expired, change status to 'Expired'
		if petition[12] < 0 and petition[7] == 'Active':
			conn1 = database.connect()
			cur1 = conn1.cursor()
			cur1.execute("UPDATE petition SET status = 'Expired' WHERE id = %s;", (petition[0],))
			conn1.commit()

			# notify the user that the petition expired
			petition_link = 'wtfprinceton.herokuapp.com/my_petitions/'+petition[1]
			email_title = 'What To Fix: Princeton - Notification'
			email_content = 'Hi '+petition[1]+',\n\nYour petition "'+petition[2]+'" did not receive enough vote and expired. You can check your petitions at '+petition_link+'.\n\nThank you for using What To Fix: Princeton!\n\nWTFPrinceton Team'
			email_from = settings.EMAIL_HOST_USER
			email_to = petition[1]+'@princeton.edu'
			send_mail(email_title, email_content, email_from, [email_to], fail_silently=True)

			tempList = list(petition)
			tempList[7] = 'Expired'
			petition = tuple(tempList)

		# add filtered petitions to list
		if query:
			petitions.append(petition)
		elif status == 'All':
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
			expiration = datetime.now()+timedelta(days=1)
			written_on = str(datetime.now())[0:10]
			cur.execute("INSERT INTO petition(netid, title, content, category, status, expiration, vote, written_on) \
				VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
				(str(request.user), str(petition.title), str(petition.content), str(petition.category),
				'Active', expiration, 0, written_on,))
			conn.commit()
			messages.success(request, 'Success! Your petition has been added!')
			return HttpResponseRedirect('../')
		context = {
			"form": form,
			"netid": str(request.user),
		}
		return render(request, 'home/create_petition.html', context)


def add_comment(request, id):
	if request.META.get('HTTP_REFERER') == None:
		return HttpResponseRedirect('../../')

	if not request.user.is_authenticated():
		return HttpResponseRedirect('../login/')
	else:
		query = request.GET.get("r")
		if query:
			conn = database.connect()
			cur = conn.cursor()
			formattedquery = '{'+query+'}'
			cur.execute("UPDATE petition SET comments = comments || %s WHERE id = %s;", (formattedquery, str(id),))
			comment_netid = '{'+str(request.user)+'}'
			cur.execute("UPDATE petition SET comment_netid = comment_netid || %s WHERE id = %s;", (comment_netid, str(id),))
			conn.commit()
			messages.success(request, 'Success! Your comment has been added!')
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
		return HttpResponseRedirect('../../login/my_petitions/'+str(netid))
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
			if petition[12] < 0 and petition[7] == 'Active':
				conn1 = database.connect()
				cur1 = conn1.cursor()
				cur1.execute("UPDATE petition SET status = 'Expired' WHERE id = %s;", (petition[0],))
				conn1.commit()

				# notify the user that the petition expired
				petition_link = 'wtfprinceton.herokuapp.com/my_petitions/'+petition[1]
				email_title = 'What To Fix: Princeton - Notification'
				email_content = 'Hi '+petition[1]+',\n\nYour petition "'+petition[2]+'" did not receive enough vote and expired. You can check your petitions at '+petition_link+'.\n\nThank you for using What To Fix: Princeton!\n\nWTFPrinceton Team'
				email_from = settings.EMAIL_HOST_USER
				email_to = petition[1]+'@princeton.edu'
				send_mail(email_title, email_content, email_from, [email_to], fail_silently=True)

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
			petitionlist.append(int(minutes+1))
			petitionlist.append("minutes")
			petition = tuple(petitionlist)
		else:
			petitionlist = list(petition)
			petitionlist.append(int(hours+1))
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

	# when user is trying to vote his own petition
	cur.execute("SELECT netid FROM petition WHERE id = %s;", (petitionid,))
	netid = cur.fetchone()[0]
	if (str(userid) == netid):
		messages.warning(request, 'You cannot vote on your own petition.')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

	# when user is trying to vote again
	cur.execute("SELECT voteid FROM petition WHERE id = %s;", (petitionid,))
	voteid = cur.fetchone()
	for listid in voteid:
		if listid != None and str(userid) in listid:
			messages.warning(request, 'You already voted on this petition.')
			return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

	# when user is trying to vote on a petition that is not active
	cur.execute("SELECT status FROM petition WHERE id = %s;", (petitionid, ))
	status = cur.fetchone()[0]
	if (str(status) != "Active"):
		messages.warning(request, 'You cannot vote because this petition is not an active petition.')
		return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
			
	cur.execute("SELECT vote FROM petition WHERE id = %s;", (petitionid,))
	vote = cur.fetchone()[0]
	now = datetime.now()
	cur.execute("SELECT expiration FROM petition WHERE id = %s;", (petitionid,))
	timeleft = cur.fetchone()[0].replace(tzinfo=None)-now

	# user votes successfully
	if vote < 10 and timeleft.days >= 0:
		formattedid = '{'+str(userid)+'}'
		cur.execute("UPDATE petition SET vote = vote+1, voteid = voteid || %s WHERE id = %s;", (formattedid, petitionid,))
		conn.commit()
		vote += 1

		if vote == 10:
			cur.execute("UPDATE petition SET status = 'Pending' WHERE id = %s;", (petitionid,))
			conn.commit()
			# notify the user that the petition reached the goal
			petition_link = 'wtfprinceton.herokuapp.com/my_petitions/'+netid
			email_title = 'What To Fix: Princeton - Notification'
			email_content = 'Hi '+netid+',\n\nCongratulations! Many students agreed with your petition "'+petition[2]+'", and your petition reached the goal. USG will soon reach out. You can check your petitions at '+petition_link+'.\n\nThank you for using What To Fix: Princeton!\n\nWTFPrinceton Team'
			email_from = settings.EMAIL_HOST_USER
			email_to = petition[1]+'@princeton.edu'
			send_mail(email_title, email_content, email_from, [email_to], fail_silently=True)

	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def instructions(request):
	if request.user.is_authenticated():
		return render(request, 'home/instructions.html', {
			'netid': request.user,
		})
	else:
		return render(request, 'home/instructions_visitor.html')


def complete_petition(request, petitionid):
	if request.META.get('HTTP_REFERER') == None:
		return HttpResponseRedirect('../')

	conn = database.connect()
	cur = conn.cursor()
	cur.execute("UPDATE petition SET status = 'Completed' WHERE id = %s;", (petitionid,))
	conn.commit()

	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))