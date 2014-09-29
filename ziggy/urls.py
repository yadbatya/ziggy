from django.conf.urls import patterns, include, url

from django.contrib import admin
from ziggy_app import views

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', views.home),
    url(r'^login/$', views.login),
    url(r'^register/$', views.register),
    url(r'^recipe/(\d+)/$', views.recipe_page),
    url(r'^add/$', views.add),
    url(r'^add/(\d+)/$', views.finish_add),
    url(r'^like/', views.like),
    url(r'^likes/(\d+)/', views.likes),
    url(r'^user/(\d+)/$', views.user_page),
    url(r'^ingredients/$', views.get_ingredients),
    # url(r'^autocomplete/$', views.autocomplete),
    url(r'^admin/', include(admin.site.urls)),
)
