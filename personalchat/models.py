from django.db import models
from django.contrib.auth.models import User

# Optional: extend user for profile info
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return self.user.username

# Private Messages
class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.sender} -> {self.receiver}'

# Optional Group Chat
class Group(models.Model):
    name = models.CharField(max_length=100)
    creator = models.ForeignKey(User, related_name='created_groups', on_delete=models.CASCADE,null=True)
    members = models.ManyToManyField(
        User, 
        related_name='chat_groups'   # <-- change this from 'groups' to something unique
    )
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name


class GroupMessage(models.Model):
    group = models.ForeignKey(Group, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='group_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read_by = models.ManyToManyField(User, related_name='read_group_messages', blank=True)

    def __str__(self):
        return f'{self.sender} -> {self.group.name}'
