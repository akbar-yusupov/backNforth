from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from chat.models import Thread

from .models import FriendshipRequest, Profile

User = get_user_model()


@receiver(post_save, sender=User)
def create_profile_signal(sender, instance, created, **kwargs):
    if created:
        new_profile = Profile.objects.create(user=instance)

        bot = User.objects.filter(username="backNforth_bot")
        if bot.exists():
            Thread.objects.create(
                first_person=new_profile,
                second_person=Profile.objects.get(user=bot.first()),
            )


@receiver(post_save, sender=FriendshipRequest)
def add_friend_signal(sender, instance, **kwargs):
    if instance.is_friends:
        Thread.objects.create(
            first_person=instance.requester, second_person=instance.requested
        )
        instance.requester.friends.add(instance.requested)
        instance.delete()
