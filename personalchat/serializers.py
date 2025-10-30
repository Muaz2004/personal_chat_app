from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Message, Group, GroupMessage

# User serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

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
