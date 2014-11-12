from django.conf.urls import patterns, url

from tests import views

urlpatterns = patterns(
    '',
    url('^$', views.PostViewSet.as_view({'get': 'list'}), name='post-list')
)
