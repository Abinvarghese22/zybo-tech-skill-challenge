"""
URL patterns for chat app.
"""
from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.user_list_view, name='user_list'),
    path('<int:user_id>/', views.chat_room_view, name='chat_room'),
    
    # API endpoints for fallback chat (AJAX/Polling)
    path('api/send_message/', views.send_message_api, name='send_message_api'),
    path('api/get_messages/<int:other_user_id>/', views.get_new_messages_api, name='get_new_messages_api'),
]
