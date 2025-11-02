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

        # Get full avatar URL
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
        serializer = self.get_serializer(msgs, many=True)
        return Response(serializer.data)

# ------------------ GROUPS ------------------
class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

class GroupMessageViewSet(viewsets.ModelViewSet):
    queryset = GroupMessage.objects.all().order_by("timestamp")
    serializer_class = GroupMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

# ------------------ PROFILE ------------------
class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView

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
