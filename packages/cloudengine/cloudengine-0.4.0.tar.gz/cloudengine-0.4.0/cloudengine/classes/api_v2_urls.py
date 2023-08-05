from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns
from cloudengine.classes.api import (ClassView, ObjectView,
                                 AppClassesView, SchemaView)


# todo: this regex puts limit on the names that classes and objects can have
urlpatterns = patterns(
    '',
    url(r'^$', AppClassesView.as_view()),
    url(r'^schema/(?P<cls>[a-zA-Z0-9]+)/$', SchemaView.as_view()),
    url(r'^(?P<cls>[a-zA-Z0-9]+)/$', ClassView.as_view()),
    url(r'^(?P<cls>[a-zA-Z0-9]+)/(?P<objid>[a-f0-9]+)/$',
        ObjectView.as_view()),
)

urlpatterns = format_suffix_patterns(urlpatterns)
