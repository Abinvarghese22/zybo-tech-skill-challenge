"""
Message model for storing chat messages between users.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class Message(models.Model):
    """
    Chat Message Model.
    Stores messages between two users with read status tracking.
    """
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name='Sender'
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name='Receiver'
    )
    content = models.TextField(verbose_name='Message Content')
    timestamp = models.DateTimeField(default=timezone.now, verbose_name='Sent At')
    is_read = models.BooleanField(default=False, verbose_name='Read Status')

    class Meta:
        ordering = ['timestamp']
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'

    def __str__(self):
        return f'{self.sender.username} → {self.receiver.username}: {self.content[:50]}'
