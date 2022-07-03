from django.urls import path

from . import views

app_name = "chat"

urlpatterns = [
    path("", views.ChatView.as_view(), name="index"),
    path("change/", views.ChangeThreadAPIView.as_view(), name="change-thread")
]
