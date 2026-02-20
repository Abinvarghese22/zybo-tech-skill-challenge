"""
Views for the chat application.
Handles user listing and chat room rendering.
Business logic is handled here, not in templates.
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max, Count, Subquery, OuterRef
from accounts.models import CustomUser
from .models import Message
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from django.utils import timezone


@login_required
def user_list_view(request):
    """
    Display all registered users except the current user.
    Shows online status and last message preview.
    """
    users = CustomUser.objects.exclude(id=request.user.id)

    # Build user data with unread count and last message preview
    user_data = []
    for user in users:
        # Get unread message count from this user
        unread_count = Message.objects.filter(
            sender=user,
            receiver=request.user,
            is_read=False
        ).count()

        # Get last message between current user and this user
        last_message = Message.objects.filter(
            Q(sender=request.user, receiver=user) |
            Q(sender=user, receiver=request.user)
        ).order_by('-timestamp').first()

        user_data.append({
            'user': user,
            'unread_count': unread_count,
            'last_message': last_message,
        })

    # Sort by last_message timestamp (most recent first), users with no messages at end
    from django.utils import timezone as tz
    import datetime
    min_dt = tz.make_aware(datetime.datetime.min + datetime.timedelta(days=1))
    user_data.sort(
        key=lambda x: x['last_message'].timestamp if x['last_message'] else min_dt,
        reverse=True
    )

    context = {
        'user_data': user_data,
    }
    return render(request, 'chat/user_list.html', context)


@login_required
def chat_room_view(request, user_id):
    """
    Display the chat room between the current user and the selected user.
    Loads message history and marks received messages as read.
    """
    other_user = get_object_or_404(CustomUser, id=user_id)

    # Prevent chatting with self
    if other_user == request.user:
        return render(request, 'chat/user_list.html', {
            'error': 'You cannot chat with yourself.'
        })

    # Get message history between the two users
    messages_qs = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by('timestamp')

    # Mark unread messages from the other user as read
    Message.objects.filter(
        sender=other_user,
        receiver=request.user,
        is_read=False
    ).update(is_read=True)

    # Generate a unique room name for the two users (alphabetically sorted IDs)
    user_ids = sorted([request.user.id, other_user.id])
    room_name = f'chat_{user_ids[0]}_{user_ids[1]}'

    context = {
        'other_user': other_user,
        'messages': messages_qs,
        'room_name': room_name,
        'current_user_id': request.user.id,
    }
    return render(request, 'chat/chat.html', context)

# --- API VIEWS FOR NON-WEBSOCKET CHAT ---

@login_required
@require_POST
def send_message_api(request):
    try:
        data = json.loads(request.body)
        receiver_id = data.get('receiver_id')
        content = data.get('message')

        if not content or not receiver_id:
            return JsonResponse({'status': 'error', 'message': 'Missing data'}, status=400)

        receiver = get_object_or_404(CustomUser, id=receiver_id)
        
        message = Message.objects.create(
            sender=request.user,
            receiver=receiver,
            content=content
        )

        return JsonResponse({
            'status': 'success',
            'message': {
                'id': message.id,
                'content': message.content,
                'timestamp': message.timestamp.strftime('%b %d, %Y %I:%M %p'),
                'sender_id': message.sender.id
            }
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def get_new_messages_api(request, other_user_id):
    other_user = get_object_or_404(CustomUser, id=other_user_id)
    
    # Get unread messages from other user
    new_messages = Message.objects.filter(
        sender=other_user,
        receiver=request.user,
        is_read=False
    ).order_by('timestamp')
    
    messages_data = []
    for msg in new_messages:
        messages_data.append({
            'type': 'chat_message',
            'message_id': msg.id,
            'message': msg.content,
            'sender_id': msg.sender.id,
            'timestamp': msg.timestamp.strftime('%b %d, %Y %I:%M %p'),
        })
        # Mark as read immediately for this simple implementation
        msg.is_read = True
        msg.save()
        
    return JsonResponse({'messages': messages_data})
