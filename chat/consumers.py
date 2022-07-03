import json

from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from accounts.models import Profile
from chat.models import Message, Thread

User = get_user_model()


class ChatConsumer(AsyncConsumer):
    async def websocket_connect(self, event):
        user = self.scope["user"]
        self.chat_room = f"user_chatroom_{user.id}"
        await self.channel_layer.group_add(self.chat_room, self.channel_name)
        await self.send({"type": "websocket.accept"})

    async def websocket_receive(self, event):
        received_data = json.loads(event["text"])
        msg = received_data.get("message")
        sent_by_id = received_data.get("sent_by")
        send_to_id = received_data.get("send_to")
        thread_id = received_data.get("thread_id")
        sent_by_profile = await self.get_profile_object(sent_by_id)
        thread_obj = await self.get_thread(thread_id)

        timestamp = timezone.localtime(
            await self.create_chat_message(thread_obj, sent_by_profile, msg)
        )
        other_user_chat_room = f"user_chatroom_{send_to_id}"
        image = await self.get_image(sent_by_profile)
        username = await self.get_username(sent_by_profile)

        response = {
            "message": msg,
            "username": username,
            "sent_by": sent_by_profile.pk,
            "thread_id": thread_id,
            "image": image,
            "updated_at": timestamp.strftime("%d %a, %H:%M"),
            "thread_updated_at": str(_("right now")),
        }

        await self.channel_layer.group_send(
            other_user_chat_room,
            {"type": "chat_message", "text": json.dumps(response)},
        )

        await self.channel_layer.group_send(
            self.chat_room,
            {"type": "chat_message", "text": json.dumps(response)},
        )

    async def websocket_disconnect(self, event):
        await self.channel_layer.group_discard(
            self.chat_room, self.channel_name
        )

    async def chat_message(self, event):
        await self.send({"type": "websocket.send", "text": event["text"]})

    @database_sync_to_async
    def get_profile_object(self, profile_id):
        qs = Profile.objects.filter(id=profile_id)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj

    @database_sync_to_async
    def get_thread(self, thread_id):
        qs = Thread.objects.filter(id=thread_id)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj

    @database_sync_to_async
    def get_username(self, profile):
        username = profile.user.username
        return username

    @database_sync_to_async
    def create_chat_message(self, thread, profile, msg):
        new_message = Message.objects.create(
            thread=thread, profile=profile, message=msg
        )
        thread = Thread.objects.get(pk=thread.pk)
        thread.updated_at = new_message.timestamp
        thread.save()
        return new_message.timestamp

    @database_sync_to_async
    def get_image(self, sent_by_profile):
        if sent_by_profile.image:
            return sent_by_profile.image.url
        else:
            return settings.CHAT_PROFILE_IMAGE_URL
