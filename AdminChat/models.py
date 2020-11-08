from django.db import models
from user.models import User 


class Message(models.Model):
    sender = models.OneToOneField(User, limit_choices_to={'is_superuser': True}, on_delete=models.CASCADE)
    content = models.TextField(max_length=1000)
    time_posted = models.DateTimeField(auto_now_add=True)
    comment = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)