"""dot360s URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.urls import include, path
from django.contrib import admin
from django.conf import settings
from django.contrib.auth import views as auth_views 
from user.api.views import ChoiceView
from feedback.api.views import FeedbackView, FeedbackDetailView


handler404 = 'user.views.error_404'
handler500 = 'user.views.error_500'
handler403 = 'user.views.error_403'
handler400 = 'user.views.error_400'


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('user/', include('user.urls')),
    path('feedback/', include('feedback.urls')),
    
    # REST-framework 
    path('api/user/', include('user.api.urls', 'user_api')),
    path('api/main/', include('main.api.urls', 'main_api')),
    path('api/choices', ChoiceView.as_view(), name="choices"),
    path('api/feedback', FeedbackView.as_view(), name="feedback"),
    path('api/feedback-detail', FeedbackDetailView.as_view(), name="feedback_detail"),

    # password management links
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(template_name="user/password_set.html"), name="password_change_done"),

    path('password-change/', auth_views.PasswordChangeView.as_view(template_name="user/password_change.html"), name="password_change"),

    path('password_reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name="user/password_reset_from_key_done.html"), name="password_reset_done"),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name="password_confirm"),

    path('password_reset/', auth_views.PasswordResetView.as_view(template_name="user/password_reset_from_key.html"), name="password_reset"),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name="user/password_reset_done.html"), name="password_reset_complete"),

]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
