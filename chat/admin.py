from django.contrib import admin

from .models import Message, Thread

admin.site.register(Message)


class MessageInline(admin.TabularInline):
    model = Message


class ThreadAdmin(admin.ModelAdmin):
    inlines = (MessageInline, )

    class Meta:
        model = Thread


admin.site.register(Thread, ThreadAdmin)
