import random

from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from timezone_field import TimeZoneField


class User(AbstractUser):
    phone_number = PhoneNumberField(
        _("Phone Number"),
        error_messages={
            "invalid": _("Enter a valid phone number (e.g. +998971234567).")
        },
    )

    REQUIRED_FIELDS = ("phone_number",)

    def save(self, *args, **kwargs):
        if not self.pk:
            if User.objects.filter(
                phone_number=self.phone_number, is_active=True
            ).count():
                raise ValidationError(
                    _("User with this phone number already exists")
                )
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")


class Code(models.Model):
    uuid = models.CharField(
        _("UUID"),
        max_length=64,
        primary_key=True,
        unique=True,
        editable=False,
    )
    owner = models.ForeignKey(
        User, verbose_name=_("Owner"), on_delete=models.CASCADE
    )
    number = models.CharField(_("Number"), max_length=6)

    def __str__(self):
        return self.number

    def save(self, *args, **kwargs):
        self.number = str(random.randint(100000, 999999))
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Code")
        verbose_name_plural = _("Codes")


class Game(models.Model):
    name = models.CharField(_("Name"), max_length=64)
    image = models.ImageField(upload_to="games/", verbose_name=_("Image"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Game")
        verbose_name_plural = _("Games")


class Profile(models.Model):
    class SkillChoices(models.IntegerChoices):
        low = 1, _("Low")
        middle = 2, _("Middle")
        high = 3, _("High")

    user = models.OneToOneField(
        User,
        verbose_name=_("User"),
        on_delete=models.CASCADE,
        related_name="profile",
    )
    age = models.PositiveSmallIntegerField(
        verbose_name=_("Age"),
        null=True,
        blank=True,
        validators=[
            validators.MinValueValidator(0),
            validators.MaxValueValidator(100),
        ],
    )
    image = models.ImageField(
        upload_to="products/%Y/%m",
        verbose_name=_("Image"),
        null=True,
        blank=True,
    )
    games = models.ManyToManyField(Game, verbose_name=_("Games"), blank=True)
    skill = models.PositiveSmallIntegerField(
        _("Skill"), choices=SkillChoices.choices, default=2
    )
    about = models.TextField(_("About"), max_length=2048)
    friends = models.ManyToManyField(
        "self", verbose_name=_("Friends"), symmetrical=True, blank=True
    )
    utc = TimeZoneField(
        use_pytz=True, verbose_name=_("UTC"), choices_display="WITH_GMT_OFFSET"
    )
    convenient_from = models.TimeField(_("From"), default="18:00:00")
    convenient_to = models.TimeField(_("To"), default="20:00:00")

    def __str__(self):
        return f"{self.age} years old user"

    class Meta:
        verbose_name = _("Profile")
        verbose_name_plural = _("Profiles")


class FriendshipRequest(models.Model):
    requester = models.ForeignKey(
        Profile,
        verbose_name=_("Requester"),
        on_delete=models.CASCADE,
        related_name="requester",
    )
    requested = models.ForeignKey(
        Profile,
        verbose_name=_("Requested"),
        on_delete=models.CASCADE,
        related_name="requested",
    )
    is_friends = models.BooleanField(_("Is friends"), default=False)

    class Meta:
        unique_together = ("requester", "requested")
        verbose_name = _("Friendship Request")
        verbose_name_plural = _("Friendship Requests")
