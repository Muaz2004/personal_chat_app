from rest_framework import viewsets, permissions, status, serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .models import Message, Group, GroupMessage, Profile
from .serializers import (
    UserSerializer,
    MessageSerializer,
    GroupSerializer,
    GroupMessageSerializer,
    ProfileSerializer
)
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView

# ------------------ USER ------------------
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


# Register user
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def register_user(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, password=password)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        "message": "Registration successful",
        "username": user.username,
        "token": token.key,
    }, status=status.HTTP_201_CREATED)


# Login user (with avatar)
@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def login_user(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)

        profile = Profile.objects.filter(user=user).first()
        avatar_url = request.build_absolute_uri(profile.avatar.url) if profile and profile.avatar else ""

        return Response({
            "message": "Login successful",
            "username": user.username,
            "token": token.key,
            "avatar": avatar_url,
        }, status=status.HTTP_200_OK)

    return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)


# ------------------ PRIVATE MESSAGES ------------------
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all().order_by("-timestamp")
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        receiver_id = self.request.data.get("receiver")
        if not receiver_id:
            raise serializers.ValidationError({"receiver": "This field is required."})
        serializer.save(sender=self.request.user, receiver_id=receiver_id)

    @action(detail=False, methods=["get"])
    def conversation(self, request):
        other_user_id = request.query_params.get("user_id")
        if not other_user_id:
            return Response({"error": "user_id query param required"}, status=400)

        msgs = Message.objects.filter(sender__id=request.user.id, receiver__id=other_user_id) | \
               Message.objects.filter(sender__id=other_user_id, receiver__id=request.user.id)
        msgs = msgs.order_by("timestamp")

        msgs.filter(receiver=request.user, read=False).update(read=True)

        serializer = self.get_serializer(msgs, many=True)
        return Response(serializer.data)


# ------------------ UNREAD COUNTS ------------------
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def unread_counts(request):
    user = request.user
    private_msgs = Message.objects.filter(receiver=user, read=False)

    unread_data = {}
    for msg in private_msgs:
        sender_id = msg.sender.id
        unread_data[sender_id] = unread_data.get(sender_id, 0) + 1

    return Response(unread_data)


# ------------------ GROUPS ------------------
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Group.objects.filter(members=self.request.user)

    def perform_create(self, serializer):
        group = serializer.save(creator=self.request.user)
        group.members.add(self.request.user)
        members_usernames = self.request.data.get("members", [])
        if members_usernames:
            users_to_add = User.objects.filter(username__in=members_usernames)
            for user in users_to_add:
                group.members.add(user)

    @action(detail=True, methods=["post"])
    def add_member(self, request, pk=None):
        group = self.get_object()
        if group.creator != request.user:
            return Response({"error": "Only the group creator can add members."},
                            status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        group.members.add(user)
        return Response({"message": f"{user.username} added to the group."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def remove_member(self, request, pk=None):
        group = self.get_object()
        if group.creator != request.user:
            return Response({"error": "Only the group creator can remove members."},
                            status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get("user_id")
        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        group.members.remove(user)
        return Response({"message": f"{user.username} removed from the group."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def leave_group(self, request, pk=None):
        group = self.get_object()
        user = request.user

        if user not in group.members.all():
            return Response({"error": "You are not a member of this group."},
                            status=status.HTTP_400_BAD_REQUEST)

        if user == group.creator:
            group.delete()
            return Response({"message": "Group deleted as creator left."}, status=status.HTTP_200_OK)

        group.members.remove(user)
        return Response({"message": f"{user.username} left the group."}, status=status.HTTP_200_OK)


# ------------------ GROUP MESSAGES ------------------
class GroupMessageViewSet(viewsets.ModelViewSet):
    queryset = GroupMessage.objects.all().order_by("timestamp")
    serializer_class = GroupMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        group_id = self.request.query_params.get("group_id")
        if group_id:
            qs = GroupMessage.objects.filter(group__id=group_id).order_by("timestamp")

            # Mark unread messages as read for current user safely
            unread_msgs = qs.exclude(sender=self.request.user).exclude(read_by=self.request.user)
            for msg in unread_msgs:
                msg.read_by.add(self.request.user)

            return qs
        return super().get_queryset()

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)


# ------------------ PROFILE ------------------
class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


# ------------------ UPDATE AVATAR ------------------
class UpdateAvatarView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request, *args, **kwargs):
        profile, created = Profile.objects.get_or_create(user=request.user)
        avatar_file = request.FILES.get('avatar')
        if not avatar_file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
        profile.avatar = avatar_file
        profile.save()
        avatar_url = request.build_absolute_uri(profile.avatar.url)
        return Response({"avatar": avatar_url}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def group_unread_counts(request):
    user = request.user
    groups = Group.objects.filter(members=user)
    unread_data = {}
    for group in groups:
        count = GroupMessage.objects.filter(
            group=group
        ).exclude(sender=user).exclude(read_by=user).count()  # only per-user unread
        unread_data[group.id] = count
    return Response(unread_data)
