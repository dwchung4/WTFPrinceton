from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

def index(request):
    return render(request, 'home/index.html')

def about(request):
	return render(request, 'home/about.html')

def contact(request):
	if request.user.is_authenticated():
		print 'authenticated'
		print request.user.id
		return render(request, 'home/contact.html')
	else:
		print 'not authenticated'
		return render(request, 'home/about.html')
