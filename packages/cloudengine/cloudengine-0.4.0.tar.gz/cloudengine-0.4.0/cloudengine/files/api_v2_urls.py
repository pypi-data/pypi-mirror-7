from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from api import FileView, FileListView


urlpatterns = patterns('',
                       url(r'^$', FileListView.as_view(), name='file-list'),
                       url(r'^(?P<filename>[a-zA-Z0-9_\.]+)/$',
                           FileView.as_view(), name='file-handler'),
                       )


urlpatterns = format_suffix_patterns(urlpatterns)
