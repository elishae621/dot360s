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
from rest_framework import routers
from rest_api import views as rest_views


router = routers.DefaultRouter()
router.register(r'users', rest_views.UserViewSet)
router.register(r'drivers', rest_views.DriverViewSet)
router.register(r'vehicle', rest_views.VehicleViewSet)
router.register(r'request', rest_views.RequestViewSet)
router.register(r'ride', rest_views.RideViewSet)
router.register(r'order', rest_views.OrderViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('user/', include('user.urls')),
    path('accounts/', include('allauth.urls')),
    path('tellme/', include('tellme.urls')),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
