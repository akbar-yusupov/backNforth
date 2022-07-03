from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import include, path
from django.views.generic import RedirectView


urlpatterns = [
    path("", RedirectView.as_view(pattern_name="chat:index"), name="index"),
    path("admin/", admin.site.urls),
    path("chat/", include("chat.urls", namespace="chat")),
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path(
        "favicon.ico",
        RedirectView.as_view(
            url=staticfiles_storage.url("images/favicon.ico")
        ),
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
