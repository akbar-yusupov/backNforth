import uuid

from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import DetailView, ListView

from .forms import LoginForm, ProfileForm, RegistrationForm
from .models import Code, FriendshipRequest, Game, Profile
from .utils import get_support_thread, send_sms

User = get_user_model()


class RegisterView(View):
    template_name = "accounts/registration/register.html"
    form_class = RegistrationForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            code = Code.objects.create(uuid=str(uuid.uuid4()), owner=user)
            request.session["code_uuid"] = code.uuid
            request.session["code_number"] = code.number
            request.session.modified = True
            send_sms(code.number, str(user.phone_number))
            return redirect("accounts:verify-phone")
        else:
            return render(request, self.template_name, {"form": form})


class VerifyPhoneView(View):
    template_name = "accounts/registration/verify_phone.html"

    def get(self, request):
        code = request.session.get("code_number", None)
        return render(request, self.template_name, {"code": code})

    def post(self, request):
        code = request.POST.get("code", None)
        code_uuid = request.session.get("code_uuid", None)
        if code and code_uuid:
            created_code = Code.objects.filter(
                uuid=code_uuid, number=code
            ).first()
            if created_code:
                created_code.owner.is_active = True
                created_code.owner.save()
                login(request, created_code.owner)
                created_code.delete()
                return redirect("accounts:profile")

        messages.add_message(
            request, messages.INFO, _("You entered the wrong code")
        )

        return self.get(request)


class LoginView(View):
    template_name = "accounts/login.html"
    form_class = LoginForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = User.objects.filter(
                username=form.cleaned_data["username"],
                phone_number=form.cleaned_data["phone_number"],
                is_active=True,
            ).first()
            if user:
                code = Code.objects.create(uuid=str(uuid.uuid4()), owner=user)
                request.session["code_uuid"] = code.uuid
                request.session.modified = True
                send_sms(code.number, str(user.phone_number))
                return redirect("accounts:verify-phone")
            else:
                messages.add_message(
                    request,
                    messages.INFO,
                    _("User with such data doesn't exists"),
                )
        return render(request, self.template_name, {"form": form})


# ↓ Profile VIEWS ↓


class ProfileView(LoginRequiredMixin, View):
    template_name = "accounts/profile/edit.html"
    form_class = ProfileForm

    @staticmethod
    def get_games(profile):
        all_games = Game.objects.all()
        preferred_games = list(
            profile.games.all().values_list("name", flat=True)
        )
        return all_games, preferred_games

    def get(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        form = self.form_class(instance=profile)
        all_games, preferred_games = self.get_games(profile)
        bot_id = User.objects.filter(username="backNforth_bot").first()
        if bot_id:
            support_thread = get_support_thread(bot_id)
        else:
            support_thread = None
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "all_games": all_games,
                "preferred_games": preferred_games,
                "support_thread": support_thread,
            },
        )

    def post(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        form = self.form_class(
            data=request.POST, files=request.FILES, instance=profile
        )

        if form.is_valid():
            form.save(commit=False)

            try:
                games = map(int, request.POST["games"])
            except ValueError:
                return self.get(request)

            games = Game.objects.filter(pk__in=games)
            form.instance.games.set(games)
            form.instance.user = request.user
            form.save()
            return self.get(request)
        else:
            all_games, preferred_games = self.get_games(profile)
            bot_id = User.objects.filter(username="backNforth_bot").first()
            if bot_id:
                support_thread = get_support_thread(bot_id)
            else:
                support_thread = None
            return render(
                request,
                self.template_name,
                {
                    "form": form,
                    "all_games": all_games,
                    "preferred_games": preferred_games,
                    "support_thread": support_thread,
                },
            )


class ForeignerProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "accounts/profile/view.html"
    context_object_name = "view_profile"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=None)
        return obj


class ProfileSearchView(LoginRequiredMixin, ListView):
    model = Profile.objects.all()
    template_name = "accounts/profile/search.html"
    context_object_name = "profiles"
    paginate_by = 10

    def get_queryset(self):
        profiles = self.model
        search = self.request.GET.get("q", None)

        if search:
            profiles = self.model.filter(user__username__icontains=search)

        return profiles.exclude(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profiles_number"] = self.get_queryset().count()
        return context


# ↓ Recommendations VIEWS ↓
class RecommendationsView(LoginRequiredMixin, View):
    template_name = "accounts/recommendations.html"

    @staticmethod
    def get_games(profile):
        all_games = Game.objects.all()
        preferred_games = list(
            profile.games.all().values_list("name", flat=True)
        )
        return all_games, preferred_games

    def get(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        requester = FriendshipRequest.objects.filter(requester=profile).values(
            "requested__pk"
        )
        requested = FriendshipRequest.objects.filter(requested=profile).values(
            "requester__pk"
        )
        recommendations = (
            Profile.objects.all()
            .exclude(
                Q(user=request.user)
                | Q(friends=profile)
                | Q(pk__in=requester)
                | Q(pk__in=requested)
            )
            .filter(skill=profile.skill, games__in=profile.games.all())
        )

        all_games, preferred_games = self.get_games(profile)
        context = {
            "recommendations": recommendations,
            "all_games": all_games,
            "preferred_games": preferred_games,
            "skill": profile.skill,
        }

        return render(request, self.template_name, context)

    def post(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        requester = FriendshipRequest.objects.filter(requester=profile).values(
            "requested__pk"
        )
        requested = FriendshipRequest.objects.filter(requested=profile).values(
            "requester__pk"
        )
        # ↓ Games filter ↓
        all_games, preferred_games = self.get_games(profile)
        try:
            games = map(int, request.POST["games"])
            games = Game.objects.filter(pk__in=games)
            recommendations = Profile.objects.filter(games__in=games)
            selected_games = games.values_list("name", flat=True)
        except ValueError:
            selected_games = preferred_games
            recommendations = Profile.objects.all()

        # ↓ Skill filter ↓
        try:
            recommendations.filter(skill=request.POST["skill"])
            selected_skill = profile.skill
        except ValueError:
            selected_skill = "any"

        all_games, preferred_games = self.get_games(profile)
        context = {
            "recommendations": recommendations.exclude(
                Q(user=request.user)
                | Q(friends=profile)
                | Q(pk__in=requester)
                | Q(pk__in=requested)
            ),
            "all_games": all_games,
            "skill": selected_skill,
            "preferred_games": selected_games,
        }

        return render(request, self.template_name, context)


class SendRequestView(LoginRequiredMixin, View):
    def post(self, request):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            profile = get_object_or_404(Profile, user=request.user)
            requested = Profile.objects.filter(pk=request.POST["pk"]).first()
            FriendshipRequest.objects.create(
                requester=profile, requested=requested
            )
            response = JsonResponse({"request_sent": True})
            return response


# ↓ ManageUsers VIEWS ↓
class ManageUsersView(LoginRequiredMixin, View):
    template_name = "accounts/manage_users.html"

    def get(self, request):
        profile = get_object_or_404(Profile, user=request.user)
        friends = profile.friends.all()  # TODO .exclude(pk=1)
        from_you = FriendshipRequest.objects.filter(
            requester=profile
        ).select_related("requested")
        to_you = FriendshipRequest.objects.filter(
            requested=profile
        ).select_related("requester")
        return render(
            request,
            self.template_name,
            {"friends": friends, "from_you": from_you, "to_you": to_you},
        )


class FriendDeleteView(LoginRequiredMixin, View):
    def post(self, request):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            profile = get_object_or_404(Profile, user=request.user)
            profile.friends.remove(request.POST["pk"])
            response = JsonResponse({"deleted": True})
            return response


class FromYouDeleteView(LoginRequiredMixin, View):
    def post(self, request):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            profile = get_object_or_404(Profile, user=request.user)
            requested = Profile.objects.get(pk=request.POST["pk"])
            FriendshipRequest.objects.filter(
                requester=profile, requested=requested
            ).delete()
            response = JsonResponse({"deleted": True})
            return response


class ToYouConfirmView(LoginRequiredMixin, View):
    def post(self, request):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            profile = get_object_or_404(Profile, user=request.user)
            requester = Profile.objects.get(pk=request.POST["pk"])
            friendship = FriendshipRequest.objects.filter(
                requester=requester, requested=profile
            ).first()
            friendship.is_friends = True
            friendship.save()
            response = JsonResponse({"deleted": True})
            return response


class ToYouDeleteView(LoginRequiredMixin, View):
    def post(self, request):
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            profile = get_object_or_404(Profile, user=request.user)
            requester = Profile.objects.get(pk=request.POST["pk"])
            FriendshipRequest.objects.filter(
                requester=requester, requested=profile
            ).delete()
            response = JsonResponse({"deleted": True})
            return response
