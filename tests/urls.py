from django.conf.urls import patterns, include, url
from rest_framework import routers

from tests import views


router = routers.SimpleRouter()

router.register("comments", views.CommentViewSet)
router.register("people", views.PersonViewSet)
router.register("posts", views.PostViewSet)
router.register(
    "nested-comments", views.NestedCommentViewSet, base_name="nested-comment")
router.register(
    "nested-posts", views.NestedPostViewSet, base_name="nested-post")
router.register("pk-comments", views.PkCommentViewSet, base_name="pk-comment")
router.register(
    "people-full", views.MaximalPersonViewSet, base_name="people-full")
router.register(
    "pk-people-full", views.PkMaximalPersonViewSet, base_name="pk-people-full")

urlpatterns = router.urls

urlpatterns += patterns(
    '',
    url('posts', include('tests.namespace_urls', namespace='n1'))
)
