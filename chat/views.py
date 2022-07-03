from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.views import View
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from accounts.models import Profile
from chat.models import Thread
from chat.serializers import MessageSerializer


class ChatView(LoginRequiredMixin, View):
    template_name = "chat/index.html"

    def get(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        threads = (
            Thread.objects.by_profile(profile=profile)
            .prefetch_related("messages")
            .order_by("-updated_at")
        )
        context = {"thread": threads.first(), "threads": threads}
        return render(request, self.template_name, context)

    def post(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        friend = get_object_or_404(Profile, pk=request.POST.get("pk", None))
        threads = (
            Thread.objects.by_profile(profile=profile)
            .prefetch_related("messages")
            .order_by("-updated_at")
        )
        message_to = get_object_or_404(
            threads, (Q(first_person=friend) | Q(second_person=friend))
        )
        context = {"thread": message_to, "threads": threads}
        return render(request, self.template_name, context)


class ChangeThreadAPIView(GenericAPIView):
    queryset = Thread.objects.all()
    serializer_class = MessageSerializer

    def post(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        if profile.image:
            profile_image = profile.image.url
        else:
            profile_image = settings.CHAT_PROFILE_IMAGE_URL
        new_thread = request.POST["new_thread"]
        new_thread = Thread.objects.get(
            Q(pk=new_thread)
            | (Q(first_person=profile) & Q(second_person=profile))
        )
        messages = new_thread.messages.all()
        created_at = timezone.localtime(new_thread.created_at).strftime(
            "%B %d, %H:%M, %Y"
        )

        if new_thread.first_person == profile:
            friend_username = new_thread.second_person.user.username
            if new_thread.second_person.image:
                friend_image = new_thread.second_person.image.url
            else:
                friend_image = settings.CHAT_PROFILE_IMAGE_URL
        else:
            friend_username = new_thread.first_person.user.username
            if new_thread.first_person.image:
                friend_image = new_thread.first_person.image.url
            else:
                friend_image = settings.CHAT_PROFILE_IMAGE_URL

        serialized_messages = self.serializer_class(messages, many=True)

        return Response(
            {
                "messages": serialized_messages.data,
                "created_at": created_at,
                "friend_username": friend_username,
                "friend_image": friend_image,
                "profile_image": profile_image,
            }
        )
