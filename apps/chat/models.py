from uuid import uuid4
from django.db import models

from apps.user.models import User


class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    initiator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='convo_starter')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='convo_participant')
    timestamp = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_sender')
    text = models.CharField(max_length=200)
    attachment = models.FileField(blank=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
