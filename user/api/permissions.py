from rest_framework import permissions 

from django.core.exceptions import PermissionDenied

from user.models import User

class IsDriver(permissions.BasePermission):
    message = "Only a driver can access this request"

    def has_permission(self, request, view):
        
        try:
            request.user.driver 
        except User.driver.RelatedObjectDoesNotExist:
            return False 
        return True