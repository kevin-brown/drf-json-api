from rest_framework import routers
from tests import views


router = routers.SimpleRouter()

router.register("comments", views.CommentViewSet)
router.register("people", views.PersonViewSet)
router.register("posts", views.PostViewSet)

urlpatterns = router.urls
