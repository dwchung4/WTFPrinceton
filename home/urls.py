from django.conf.urls import url
from . import views
from cas import views as cas_views
from django.core.handlers.wsgi import WSGIRequest
from django import http
from django.http import HttpResponse
from django.http import HttpRequest
from StringIO import StringIO
from django.test.client import RequestFactory

app_name = 'home'

#<WSGIRequest: GET '/login/'>

request = HttpRequest()
request.method = 'GET'
request.path = '/login/'
print 'request: ',
print request
#b = WSGIRequest(request)
#print b

"""
a = WSGIRequest({
		'REQUEST_METHOD': 'GET',
		'PATH_INFO': '/',
		'wsgi.input': StringIO(),
	})
print 'WSGI: ',
print a
"""

environ = RequestFactory().get('/').environ
c = WSGIRequest(environ)
print c
print c.__dict__

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^about/$', views.about, name='about'),
    url(r'^login/$', 'cas.views.login', name='login'),
    #url(r'^login/$', cas_views.login(request=c, next_page=False, required=False, gateway=False), name='login'),
	url(r'^logout/$', 'cas.views.logout', name='logout'),
	url(r'^create_petition/$', views.create_petition, name='create_petition'),
	url(r'^(?P<netid>[0-9a-z]+)/$', views.my_petitions, name='my_petitions'),
]


