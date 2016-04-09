from django.conf.urls import url
from . import views

app_name = 'home'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^about/$', views.about, name='about'),
    url(r'^login/$', 'cas.views.login', name='login'),
	url(r'^logout/$', 'cas.views.logout', name='logout'),
	url(r'^create_petition/$', views.create_petition, name='create_petition'),
	url(r'^(?P<netid>[0-9a-z]+)/$', views.my_petitions, name='my_petitions'),
]