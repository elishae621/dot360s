from rest_framework import serializers 
from feedback.models import Feedback


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback 
        fields = ['pk', 'user', 'details', 'happy', 'date']