from django.contrib import admin
from AdminChat.models import Message


class MessageInline(admin.TabularInline):
    model = Message


class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'time_posted', 'content')
    list_filter = ('sender',)
    inlines = [MessageInline, ]
    fieldsets = (
        ('None', {
            'classes': ('wide',),
            'fields': ('sender', 'content', ),
        }),
    )
    search_fields = ('sender', 'content',)
    ordering = ('time_posted', )


admin.site.register(Message, MessageAdmin)