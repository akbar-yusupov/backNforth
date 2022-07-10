from django import forms
from django.contrib.auth import get_user_model
from django.core.files.images import get_image_dimensions
from django.utils.translation import gettext_lazy as _
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from timezone_field import TimeZoneFormField

from . import models

User = get_user_model()


class RegistrationForm(forms.ModelForm):
    phone_number = PhoneNumberField(
        label=_("Phone Number"),
        required=True,
        widget=PhoneNumberPrefixWidget(
            {
                "class": "form-control mb-3 fw-bold",
                "placeholder": _("Enter your phone number"),
            }
        ),
        error_messages={
            "invalid": _("Enter a valid phone number (e.g. +998971234567).")
        },
    )
    username = forms.CharField(
        label=_("Username"),
        widget=forms.TextInput(
            {
                "class": "form-control mb-3 fw-bold",
                "placeholder": _("Enter your username"),
            }
        ),
    )

    def clean_phone_number(self):
        phone_number = self.cleaned_data["phone_number"]
        if User.objects.filter(
            phone_number=phone_number, is_active=True
        ).count():
            raise forms.ValidationError(
                _("User with this phone number already exists")
            )
        return phone_number

    class Meta:
        model = models.User
        fields = ("username", "phone_number")


class LoginForm(forms.Form):
    phone_number = PhoneNumberField(
        label=_("Phone Number"),
        required=True,
        widget=PhoneNumberPrefixWidget(
            {
                "class": "form-control mb-3 fw-bold",
                "placeholder": _("Enter your phone number"),
            }
        ),
        error_messages={
            "invalid": _("Enter a valid phone number (e.g. +998971234567).")
        },
    )
    username = forms.CharField(
        label=_("Username"),
        widget=forms.TextInput(
            {
                "class": "form-control mb-3 fw-bold",
                "placeholder": _("Enter your username"),
            }
        ),
    )


class ProfileForm(forms.ModelForm):
    __MIN_WIDTH = 300
    __MIN_HEIGHT = 300

    image = 1
    age = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={"min": "1", "max": 100, "class": "form-control mb-3"},
        )
    )
    utc = TimeZoneFormField(label=_("UTC"), choices_display="WITH_GMT_OFFSET")
    convenient_from = forms.TimeField(widget=forms.TimeInput(format="%H:%M"))
    convenient_to = forms.TimeField(widget=forms.TimeInput(format="%H:%M"))
    about = forms.CharField(
        max_length=2048,
        widget=forms.Textarea(attrs={"class": "form-control mb-4", "rows": 5}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["skill"].widget.attrs.update(
            {"class": "form-control mb-3"}
        )
        self.fields["utc"].widget.attrs.update({"class": "form-control mb-3"})
        self.fields["convenient_from"].widget.attrs.update(
            {"class": "form-control mb-3"}
        )
        self.fields["convenient_to"].widget.attrs.update(
            {"class": "form-control mb-3"}
        )
        self.fields["user"].required = False

    def clean_image(self):
        image = self.cleaned_data.get("image", None)
        if image:
            width, height = get_image_dimensions(image)
            if width < self.__MIN_WIDTH or height < self.__MIN_HEIGHT:
                raise forms.ValidationError(
                    f"The image should be at least {self.__MIN_WIDTH}px to "
                    f"{self.__MIN_HEIGHT}px, not {width}px to {height}px"
                )
        return image

    class Meta:
        model = models.Profile
        fields = (
            "user",
            "age",
            "image",
            "games",
            "skill",
            "about",
            "utc",
            "convenient_from",
            "convenient_to",
        )
