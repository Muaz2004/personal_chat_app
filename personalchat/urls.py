from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    MessageViewSet,
    GroupViewSet,
    GroupMessageViewSet,
    register_user,
    login_user,
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'messages', MessageViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'group-messages', GroupMessageViewSet)

urlpatterns = [
    path('api/register/', register_user, name='register_user'),
    path('api/login/', login_user, name='login_user'),
    path('api/', include(router.urls)),
]
