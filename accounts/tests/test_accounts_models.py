import pytest
from django.core.exceptions import ValidationError


def test_user_str(user):
    assert str(user) == "admin"


def test_user_phone_number(user, user_factory):
    with pytest.raises(ValidationError) as e:
        user_factory.create(
            email="new@new.com",
            username="new",
            phone_number=user.phone_number,
            password="new",
            is_active=True,
        )
    assert str(e.value) == "['User with this phone number already exists']"


def test_code_str(code):
    assert len(str(code)) == 6


def test_game_str(game):
    assert str(game) == "game1"


# def test_profile_str(profile):
#     assert str(profile) == "18 years old user"
