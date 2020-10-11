from django.db import models

from userauth.models import UserModel
# Create your models here.

class ChatModel(models.Model):
    sender = models.ForeignKey(UserModel, related_name='sender', unique=False, on_delete=models.CASCADE, blank=False)
    reciever = models.ForeignKey(UserModel, related_name='reciever', unique=False, on_delete=models.CASCADE, blank=False)
    message = models.CharField(max_length=120, blank=False)
    send_date = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False, blank=False)
    def __str__(self):
        return f"{self.sender} => {self.reciever}"
    
    def is_exists(self):
        return self != None

class BlockingModel(models.Model):
    username = models.ForeignKey(UserModel, related_name='blocker', unique=False, on_delete=models.CASCADE, blank=False)
    blocked_user = models.ForeignKey(UserModel, related_name='blocked', unique=False, on_delete=models.CASCADE, blank=False)


    def is_blocked(self):
        return BlockingModel.objects.filter(username=self.username, blocked_user=self.blocked_user).count() > 0

    def self_terminate(self):
        return self.delete()


class LogModel(models.Model):
    error_message = models.CharField(max_length=500, blank=False)
    location = models.CharField(max_length=500, blank=False)
    responsible_user = models.ForeignKey(UserModel, related_name='responsible', on_delete=models.CASCADE, null=True, blank=True)
    error_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.error_message



class EventLogModel(models.Model):
    event = models.CharField(max_length=500, blank=False)
    user = models.ForeignKey(UserModel, related_name='user', on_delete=models.CASCADE, null=True, blank=True)
    happened_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.event
