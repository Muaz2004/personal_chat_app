from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Message, Group, GroupMessage, Profile

# User serializer
class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'avatar']

    def get_avatar(self, obj):
        request = self.context.get("request")
        profile = getattr(obj, "profile", None) or Profile.objects.filter(user=obj).first()
        if profile and profile.avatar:
            return request.build_absolute_uri(profile.avatar.url) if request else profile.avatar.url
        return ""

# Profile serializer
class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['username', 'avatar']

    def get_avatar(self, obj):
        request = self.context.get("request")
        if obj.avatar:
            return request.build_absolute_uri(obj.avatar.url) if request else obj.avatar.url
        return ""

# Private message serializer
class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'content', 'timestamp', 'read']

# Group serializer
class GroupSerializer(serializers.ModelSerializer):
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'members', 'created_at']

# Group message serializer
class GroupMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    group = GroupSerializer(read_only=True)

    class Meta:
        model = GroupMessage
        fields = ['id', 'group', 'sender', 'content', 'timestamp']
