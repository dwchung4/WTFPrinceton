from django.conf.urls import include, url
from django.contrib import admin
from . import views

app_name = 'home'

urlpatterns = [
    # Examples:
    # url(r'^$', 'myproject.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.index, name='index')
]
