from django.conf.urls import patterns, include, url
from django.contrib import admin

from bookmarks import views

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'mysite.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^register/$', views.register),
    url(r'^oauth/authcode$', views.authcode),
    url(r'^oauth/token$', views.handleTokenRequest),
    url(r'^bookmarks$', views.handleBookmarksRequest),
    url(r'^me$', views.handleMeRequest),
    url(r'^status$', views.handleStatusRequest),
    url(r'^bookmarks/(?P<page>\d{1,4})$', views.handleBookmarksPaginationRequest),
    url(r'^bookmarks/detail/(?P<id>\d{1,4})$', views.handleDetailRequest),
)
