from django.contrib.auth.views import LogoutView
from django.urls import path, reverse_lazy

from . import views

app_name = "accounts"

urlpatterns = [
    # ↓ Registration and Authorization URLS ↓
    path("register", views.RegisterView.as_view(), name="register"),
    path("verify-phone", views.VerifyPhoneView.as_view(), name="verify-phone"),
    path("login", views.LoginView.as_view(), name="login"),
    path(
        "logout",
        LogoutView.as_view(next_page=reverse_lazy("accounts:login")),
        name="logout",
    ),
    # ↓ Profile URLS ↓
    path(
        "<int:pk>",
        views.ForeignerProfileDetailView.as_view(),
        name="view-profile",
    ),
    path("profile", views.ProfileView.as_view(), name="profile"),
    path("search", views.ProfileSearchView.as_view(), name="search"),
    # ↓ Recommendations URLS ↓
    path(
        "recommendations",
        views.RecommendationsView.as_view(),
        name="recommendations",
    ),
    path("send-request", views.SendRequestView.as_view(), name="send-request"),
    # ↓ Manage-users URLS ↓
    path("manage-users", views.ManageUsersView.as_view(), name="manage-users"),
    path(
        "friend-delete", views.FriendDeleteView.as_view(), name="friend-delete"
    ),
    path(
        "from-you-delete",
        views.FromYouDeleteView.as_view(),
        name="from-you-delete",
    ),
    path(
        "to-you-confirm",
        views.ToYouConfirmView.as_view(),
        name="to-you-confirm",
    ),
    path(
        "to-you-delete", views.ToYouDeleteView.as_view(), name="to-you-delete"
    ),
]
