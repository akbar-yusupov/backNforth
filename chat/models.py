from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from accounts.models import Profile


class ThreadManager(models.Manager):
    def by_profile(self, **kwargs):
        profile = kwargs.get("profile")
        lookup = Q(first_person=profile) | Q(second_person=profile)
        qs = self.get_queryset().filter(lookup).distinct()
        return qs


class Thread(models.Model):
    first_person = models.ForeignKey(
        Profile,
        verbose_name=_("First Person"),
        on_delete=models.CASCADE,
        related_name="first_person",
    )
    second_person = models.ForeignKey(
        Profile,
        verbose_name=_("Second Person"),
        on_delete=models.CASCADE,
        related_name="second_person",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Created at")
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Updated at")
    )

    objects = ThreadManager()

    class Meta:
        verbose_name = _("Thread")
        verbose_name_plural = _("Threads")
        unique_together = ("first_person", "second_person")


class Message(models.Model):
    thread = models.ForeignKey(
        Thread,
        verbose_name=_("Thread"),
        on_delete=models.CASCADE,
        related_name="messages",
    )
    profile = models.ForeignKey(
        Profile, verbose_name=_("Profile"), on_delete=models.CASCADE
    )
    message = models.TextField(verbose_name=_("Message"))
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")
