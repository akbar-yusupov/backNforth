from django.contrib import admin

from . import models

admin.site.register(models.User)
admin.site.register(models.Code)

admin.site.register(models.Profile)
admin.site.register(models.Game)


admin.site.register(models.FriendshipRequest)
