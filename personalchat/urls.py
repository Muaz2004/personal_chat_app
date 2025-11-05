from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    UpdateAvatarView,
    UserViewSet,
    MessageViewSet,
    GroupViewSet,
    GroupMessageViewSet,
    ProfileViewSet,
    group_unread_counts,   # <-- added
    register_user,
    login_user,
    unread_counts,
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'messages', MessageViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'group-messages', GroupMessageViewSet)
router.register(r'profiles', ProfileViewSet, basename='profile')  # <-- added

urlpatterns = [
    path('api/register/', register_user, name='register_user'),
    path('api/login/', login_user, name='login_user'),
   
    path('api/profile/avatar/', UpdateAvatarView.as_view(), name='update_avatar'),
    path('api/messages/unread_counts/', unread_counts, name='unread-counts'),
    path('api/group-messages/unread_counts/', group_unread_counts, name='group-unread-counts'),
    #path('test-profile/', test_profile_api, name='test_profile_api'),
    path('api/', include(router.urls)),
]
