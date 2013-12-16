from django.conf.urls.defaults import patterns, url, include
from django.views.generic import ListView
from stories.models import Book
import views
import registrationviews
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login, logout

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', ListView.as_view(model=Book)),
    url(r'^books/(?P<pk>\d+)/$', views.home),
    url(r'^login/$', login),
    url(r'^logout/$', logout, {'next_page': '/'}),
    url(r'^register/$', registrationviews.register),
    url(r'^accounts/profile/$', views.profile),
    url(r'^page:(\d+)/$', views.page),
    url(r'^writenextpage:(\d+)/(\d+)/$', views.writenextpage),
    url(r'^submitnewpage:(\d+)/(\d+)/$', views.submitnewpage),
    url(r'^editpage:(\d+)/$', views.editpage),
    url(r'^submiteditedpage:(\d+)/$', views.submiteditedpage),
    url(r'^deletebranch:(\d+)/$', views.deletebranch),
    url(r'^viewtree:(\d+)/$', views.viewtree),

    url(r'^page;404/$', views.page404),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    url(r'^tinymce/', include('tinymce.urls')),
)
