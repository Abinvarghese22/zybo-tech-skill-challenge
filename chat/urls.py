"""
URL patterns for chat app.
"""
from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.user_list_view, name='user_list'),
    path('<int:user_id>/', views.chat_room_view, name='chat_room'),
]
