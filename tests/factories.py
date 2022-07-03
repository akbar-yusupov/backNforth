import datetime

import factory
from django.core.files.base import ContentFile
from faker import Faker

from accounts.models import Code, Game, Profile, User
from chat.models import Thread

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):

    email = "admin@admin.com"
    username = "admin"
    phone_number = "+998991234567"
    password = "admin"
    is_active = True
    is_staff = False

    class Meta:
        model = User


class CodeFactory(factory.django.DjangoModelFactory):

    uuid = "458c455f-fb17-4e1b-bc12-34ced0f9093f"
    owner = factory.SubFactory(UserFactory)
    number = "123456"

    class Meta:
        model = Code


class GameFactory(factory.django.DjangoModelFactory):

    name = "game1"
    image = factory.LazyAttribute(
        lambda _: ContentFile(
            factory.django.ImageField()._make_data(
                {"width": 1024, "height": 768}
            ),
            "example.jpg",
        )
    )

    class Meta:
        model = Game


class ProfileFactory(factory.django.DjangoModelFactory):
    # user = factory.RelatedFactory(UserFactory)
    age = 18
    image = factory.LazyAttribute(
        lambda _: ContentFile(
            factory.django.ImageField()._make_data(
                {"width": 1024, "height": 768}
            ),
            "example.jpg",
        )
    )
    games = factory.RelatedFactory(GameFactory)
    skill = 2
    about = "about info..."
    # friends
    # utc
    convenient_from = datetime.time(18, 0)
    convenient_to = datetime.time(20, 0)

    class Meta:
        model = Profile


class ThreadFactory(factory.django.DjangoModelFactory):
    first_person = factory.RelatedFactory(ProfileFactory)
    second_person = factory.RelatedFactory(ProfileFactory)
    created_at = datetime.datetime(2022, 6, 28, 18, 28, 41, 441006)
    updated_at = datetime.datetime(2022, 6, 28, 18, 28, 41, 441007)

    class Meta:
        model = Thread
