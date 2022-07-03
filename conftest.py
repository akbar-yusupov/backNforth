import pytest
from pytest_factoryboy import register

from tests.factories import (
    CodeFactory,
    GameFactory,
    ProfileFactory,
    ThreadFactory,
    UserFactory,
)

register(UserFactory)
register(CodeFactory)
register(GameFactory)
register(ProfileFactory)
register(ThreadFactory)


@pytest.fixture
def user(db, user_factory):
    new_user = user_factory.create()
    return new_user


@pytest.fixture
def code(db, code_factory):
    new_code = code_factory.create()
    return new_code


@pytest.fixture
def game(db, game_factory):
    new_game = game_factory.create()
    return new_game


@pytest.fixture
def profile(db, profile_factory):
    new_profile = profile_factory.create()
    return new_profile


@pytest.fixture
def thread(db, thread_factory):
    new_factory = thread_factory.create()
    return new_factory
