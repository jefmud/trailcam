"""deertrap URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^demo/$', views.demo, name='demo'),
    url(r'^sites/$', views.SiteListView.as_view(), name='site_list_view'),
    url(r'^site/(?P<pk>\w+)/$', views.SiteDetailView.as_view(), name='site_detail_view'),
    url(r'^site_images/(?P<pk>\d+)/$', views.site_images, name='site_images'),
    #url(r'^images/$', views.ImageListView.as_view(), name='image_list_view'),
    url(r'images/$', views.all_images, name='image_list_view'),
    url(r'^image/(?P<pk>\d+)/$', views.ImageDetailView.as_view(), name='image_detail_view'),
    url(r'^image_observations/(?P<pk>\d+)/$', views.image_observations, name='image_observations'),
    url(r'^image_observation_form/(?P<pk>\d+)/$', views.image_observation_form, name='image_observation_form'),
    url(r'^observation_form/(?P<pk>\d+)/$', views.observation_form, name='observation_form'),
    url(r'^observation/(?P<pk>\d+)/edit/$', views.observation_edit, name='observation_edit'),
    url(r'^observation/(?P<pk>\d+)/$', views.ObservationDetailView.as_view(), name='observation_detail_view'),
    url(r'^searchbox/$', views.searchbox, name='searchbox'),
    url(r'^todo_create/$', views.todo_create, name='todo_create'),
    url(r'^todo_clear/$', views.todo_clear, name='todo_clear'),
    url(r'todo_list/$', views.todo_list, name='todo_list'),
    url(r'todo_list/(?P<username>\w+)/$', views.todo_list, name='todo_list'),
    url(r'^todo_detail/(?P<pk>\d+)/$', views.todo_list, name='todo_detail'),
    ]