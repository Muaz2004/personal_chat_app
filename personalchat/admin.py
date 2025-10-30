from django.contrib import admin
from .models import Profile, Message, Group, GroupMessage

admin.site.register(Profile)
admin.site.register(Message)
admin.site.register(Group)
admin.site.register(GroupMessage)
