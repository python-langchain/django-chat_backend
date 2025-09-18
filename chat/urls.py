from django.urls import path
from . import views

urlpatterns = [
    path("start/", views.start_chat, name="start_chat"),
    path("chats/", views.list_chats, name="list_chats"),
    path("chats/<int:chat_id>/messages/", views.messages_view, name="messages"),
]
