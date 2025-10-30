from rest_framework import viewsets, permissions
from django.contrib.auth.models import User
from .models import Message, Group, GroupMessage
from .serializers import UserSerializer, MessageSerializer, GroupSerializer, GroupMessageSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

# Users
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

# Private Messages
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().order_by('-timestamp')
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    # List messages between two users
    @action(detail=False, methods=['get'])
    def conversation(self, request):
        other_user_id = request.query_params.get('user_id')
        if not other_user_id:
            return Response({"error": "user_id query param required"}, status=400)
        msgs = Message.objects.filter(
            sender__id=request.user.id, receiver__id=other_user_id
        ) | Message.objects.filter(
            sender__id=other_user_id, receiver__id=request.user.id
        )
        msgs = msgs.order_by('timestamp')
        serializer = self.get_serializer(msgs, many=True)
        return Response(serializer.data)

# Groups
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

# Group Messages
class GroupMessageViewSet(viewsets.ModelViewSet):
    queryset = GroupMessage.objects.all().order_by('timestamp')
    serializer_class = GroupMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
