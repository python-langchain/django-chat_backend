"""
Django admin configuration for chat application.

This module configures the Django admin interface for chat models.
Currently no models are registered for admin access, but this can be
extended to provide admin management of chats and messages if needed.
"""

from django.contrib import admin

# Register your models here.
# 
# To enable admin management of chat models, uncomment and customize:
# 
# from .models import Chat, Message
# 
# @admin.register(Chat)
# class ChatAdmin(admin.ModelAdmin):
#     list_display = ['id', 'created_at', 'updated_at']
#     filter_horizontal = ['participants']
# 
# @admin.register(Message) 
# class MessageAdmin(admin.ModelAdmin):
#     list_display = ['id', 'chat', 'sender', 'created_at']
#     list_filter = ['created_at']
