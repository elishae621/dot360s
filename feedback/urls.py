from django.urls import path 
from feedback.views import FeedbackFormView 
 
app_name = 'form'
urlpatterns = [
    path('', FeedbackFormView.as_view(), name='home'),
]