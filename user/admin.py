from django.contrib import admin
from user.models import (
    User, Driver, Vehicle, Request, Ride, Order
)
from django.contrib.auth.admin import UserAdmin


# the follow code will append the user Driver inline at the bottom of
# the user 's models and not place it in a seperate models like the main
# User model.
class UserInline(admin.StackedInline):
    model = Driver
    can_delete = False
    verbose_name_plural = 'Driver'
    fk_name = 'user'


# add the custom models to django admin
# also include cusomisation features for the interface
class UserAdminConfig(UserAdmin):
    model = User
    # add the Driver inline to the User model
    inlines = (UserInline, )
    search_fields = ('email', 'firstname',)
    list_filter = ('email', 'firstname', 'is_driver', 'is_active', 'is_staff')
    ordering = ('firstname',)
    list_display = ('email', 'firstname', 'lastname','is_driver',  'is_active', 'is_staff',)
    fieldsets = (
        (None, {'fields': ('email', 'firstname',)}),
        ('Permissions', {'fields': ('is_staff', 'is_driver', 'is_active',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'firstname', 'lastname', 'password1', 'password2', 'is_active', 'is_staff')
        }),
    )

class VehicleInline(admin.StackedInline):
    model = Vehicle
    can_delete = True
    verbose_name_plural = 'Vehicle'
    fk_name = 'owner'


class DriverAdminConfig(admin.ModelAdmin):
    model = Driver
    # add the Driver inline to the User model
    inlines = (VehicleInline, )
    search_fields = ('user', 'location', 'status', 'journey_type')
    list_filter = ('user', 'status', 'journey_type', 'location')
    ordering = ('location',)
    list_display = ('user', 'status', 'journey_type', 'location')
    fieldsets = (
        (None, {'fields': ('user',)}),
        ('Details', {'fields': ('status', 'location', 'journey_type',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user', 'image', 'status', 'journey_type', 'location',)
        }),
    )

class OrderAdmin(admin.ModelAdmin):
    list_display = ('request', 'driver', 'time_posted', 'accepted,')
    
admin.site.register(User, UserAdminConfig)
admin.site.register(Driver, DriverAdminConfig)
admin.site.register(Request)
admin.site.register(Ride)
admin.site.register(Order)