from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("", views.list_users, name="users_list"),
]
