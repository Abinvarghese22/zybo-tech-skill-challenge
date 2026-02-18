"""
WebSocket Consumer for real-time chat.
Handles message sending/receiving, typing indicators,
read receipts, message deletion, and online status.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Async WebSocket consumer for private chat between two users.
    Handles: chat messages, typing indicators, read receipts, message deletion.
    """

    async def connect(self):
        """Accept connection only for authenticated users."""
        self.user = self.scope['user']

        # Only authenticated users can connect via WebSocket
        if self.user.is_anonymous:
            await self.close()
            return

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Update user online status
        await self.set_user_online(True)

        await self.accept()

        # Notify the room that user is online
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_status',
                'user_id': self.user.id,
                'username': self.user.username,
                'is_online': True,
            }
        )

    async def disconnect(self, close_code):
        """Leave room group and update status on disconnect."""
        if hasattr(self, 'room_group_name'):
            # Update user online status
            await self.set_user_online(False)

            # Notify the room that user went offline
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_status',
                    'user_id': self.user.id,
                    'username': self.user.username,
                    'is_online': False,
                }
            )

            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """
        Handle incoming WebSocket messages.
        Supports: chat_message, typing, mark_read, delete_message
        """
        data = json.loads(text_data)
        message_type = data.get('type', 'chat_message')

        if message_type == 'chat_message':
            content = data.get('message', '').strip()

            # Prevent empty messages
            if not content:
                return

            receiver_id = data.get('receiver_id')

            # Save message to database
            message_obj = await self.save_message(receiver_id, content)

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message_id': message_obj['id'],
                    'message': content,
                    'sender_id': self.user.id,
                    'sender_username': self.user.username,
                    'receiver_id': receiver_id,
                    'timestamp': message_obj['timestamp'],
                    'is_read': False,
                }
            )

        elif message_type == 'typing':
            # Send typing indicator to the room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'typing_indicator',
                    'user_id': self.user.id,
                    'username': self.user.username,
                    'is_typing': data.get('is_typing', False),
                }
            )

        elif message_type == 'mark_read':
            # Mark messages as read
            sender_id = data.get('sender_id')
            await self.mark_messages_read(sender_id)

            # Notify the sender that messages were read
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'messages_read',
                    'reader_id': self.user.id,
                    'sender_id': sender_id,
                }
            )

        elif message_type == 'delete_message':
            message_id = data.get('message_id')
            deleted = await self.delete_message(message_id)

            if deleted:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'message_deleted',
                        'message_id': message_id,
                        'deleted_by': self.user.id,
                    }
                )

    # ---- Group message handlers ----

    async def chat_message(self, event):
        """Send chat message to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message_id': event['message_id'],
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'receiver_id': event['receiver_id'],
            'timestamp': event['timestamp'],
            'is_read': event['is_read'],
        }))

    async def typing_indicator(self, event):
        """Send typing indicator to WebSocket."""
        # Don't send typing indicator to the person who is typing
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user_id': event['user_id'],
                'username': event['username'],
                'is_typing': event['is_typing'],
            }))

    async def messages_read(self, event):
        """Send read receipt notification to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'messages_read',
            'reader_id': event['reader_id'],
            'sender_id': event['sender_id'],
        }))

    async def user_status(self, event):
        """Send user online/offline status to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'user_status',
            'user_id': event['user_id'],
            'username': event['username'],
            'is_online': event['is_online'],
        }))

    async def message_deleted(self, event):
        """Send message deletion notification to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'message_deleted',
            'message_id': event['message_id'],
            'deleted_by': event['deleted_by'],
        }))

    # ---- Database operations (sync_to_async) ----

    @database_sync_to_async
    def save_message(self, receiver_id, content):
        """Save a chat message to the database."""
        from accounts.models import CustomUser
        from .models import Message

        receiver = CustomUser.objects.get(id=receiver_id)
        message = Message.objects.create(
            sender=self.user,
            receiver=receiver,
            content=content,
        )
        return {
            'id': message.id,
            'timestamp': message.timestamp.strftime('%b %d, %Y %I:%M %p'),
        }

    @database_sync_to_async
    def mark_messages_read(self, sender_id):
        """Mark all messages from a sender to this user as read."""
        from .models import Message
        Message.objects.filter(
            sender_id=sender_id,
            receiver=self.user,
            is_read=False
        ).update(is_read=True)

    @database_sync_to_async
    def set_user_online(self, is_online):
        """Update user online status and last_seen."""
        from accounts.models import CustomUser
        CustomUser.objects.filter(id=self.user.id).update(
            is_online=is_online,
            last_seen=timezone.now()
        )

    @database_sync_to_async
    def delete_message(self, message_id):
        """Delete a message (only if the current user is the sender)."""
        from .models import Message
        try:
            message = Message.objects.get(id=message_id, sender=self.user)
            message.delete()
            return True
        except Message.DoesNotExist:
            return False
