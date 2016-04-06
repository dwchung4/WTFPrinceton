from django.conf.urls import url
from . import views
import django_cas

app_name = 'home'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^about/$', views.about, name='about'),
    url(r'^contact/$', views.contact, name='contact'),
    url(r'^admin/login/$', 'cas.views.login', name='login'),
	url(r'^admin/logout/$', 'cas.views.logout', name='logout'),
]