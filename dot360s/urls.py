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
from django.urls import include, path, re_path
from django.contrib import admin
from django.conf import settings
from rest_framework import routers
from rest_api import views as rest_views
from rest_framework.authtoken import views
from allauth.account.views import confirm_email


handler404 = 'user.views.error_404'
handler500 = 'user.views.error_500'
handler403 = 'user.views.error_403'
handler400 = 'user.views.error_400'


router = routers.DefaultRouter()
router.register(r'users', rest_views.UserViewSet)
router.register(r'drivers', rest_views.DriverViewSet)
router.register(r'vehicle', rest_views.VehicleViewSet)
router.register(r'request', rest_views.RequestViewSet)
router.register(r'ride', rest_views.RideViewSet)
router.register(r'order', rest_views.OrderViewSet)
router.register(r'withdrawal', rest_views.WithdrawalViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('user/', include('user.urls')),
    path('accounts/', include('allauth.urls')),
    path('tellme/', include('tellme.urls')),

    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # path('api-auth/registration/', include('rest_framework.registration.urls')),
    # re_path(r'^accounts-rest/registration/account-confirm-email/(?P<key>.+)/$', confirm_email, name='account_confirm_email'),
    path('api-token-auth/', views.obtain_auth_token, name='api-token-auth'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
