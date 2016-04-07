from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .forms import PetitionForm
from .models import Petition

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
			petition.user = request.user
			petition.save()
			return render(request, 'home/index.html', {'petition': petition})
		context = {
			"form": form,
			"username": request.user,
		}
		return render(request, 'home/create_petition.html', context)