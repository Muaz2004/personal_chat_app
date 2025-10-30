from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, MessageViewSet, GroupViewSet, GroupMessageViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'messages', MessageViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'group-messages', GroupMessageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
