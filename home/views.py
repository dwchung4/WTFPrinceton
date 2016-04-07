from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q

def index(request):
	return render(request, 'home/index.html')

def about(request):
	return render(request, 'home/about.html')

def contact(request):
	return render(request, 'home/contact.html')

def create_petition(request):
	return render(request, 'home/create_petition.html')