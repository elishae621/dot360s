from django.contrib import admin
from feedback.models import Feedback



class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'details', 'date', 'happy',)
    list_filter = ('date', 'happy',)
    search_fields = ('user', 'details',)

    class Meta:
        model = Feedback


admin.site.register(Feedback, FeedbackAdmin)