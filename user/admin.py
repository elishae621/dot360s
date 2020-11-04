from django.contrib import admin
from user.models import (
    User, Driver, Vehicle, Request, Ride, Order
)
from django.contrib.auth.models import Group
from django.contrib import messages


class DriverInline(admin.StackedInline):
    model = Driver


class VehicleInline(admin.StackedInline):
    model = Vehicle


class UserAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'lastname', 'phone', 'account_balance', 'is_driver', 'is_staff')
    list_filter = ('firstname', 'is_driver')
    inlines = [DriverInline, ]
    readonly_fields = ('account_balance', 'is_driver', 'is_staff')
    fieldsets = (
        ('Personal Information', {
            'classes': ('wide',),
            'fields': (('firstname', 'lastname'), 'email', 'phone', ),
        }),
        ('Account', {
            'classes': ('wide',),
            'fields': ('account_balance',),
        }),
        ('Permissions', {
            'classes': ('wide',),
            'fields': ('is_driver', 'is_staff',),
        }),
    )
    search_fields = ('firstname',)
    ordering = ('firstname',)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(UserAdmin, self).get_inline_instances(request, obj)


    def driver(self, obj):
        return obj.is_driver == 1

    driver.boolean = True

    def make_driver(modelAdmin, request, queryset):
        queryset.update(is_driver = 1)
        messages.success(request, "Selected User(s) Marked as drivers Successfully !!")

    def make_not_driver(modelAdmin, request, queryset):
        queryset.update(is_driver = 0)
        messages.success(request, "Selected user(s) Marked as non drivers Successfully !!")

    admin.site.add_action(make_driver, "Make Driver")
    admin.site.add_action(make_not_driver, "Make Not Driver")

    def has_add_permission(self, request):
        return False

class DriverAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'status', 'journey_type')
    list_filter = ('location', 'status', 'journey_type')
    readonly_fields = ('user',)
    inlines = [VehicleInline, ]    
    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user',),
        }),
        ('Details', {
            'classes': ('wide',),
            'fields': ('location', 'status', 'journey_type',),

        }),
    )
    search_fields = ('location', 'status', 'journey_type',)
    ordering = ('location',)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(DriverAdmin, self).get_inline_instances(request, obj)

    def has_add_permission(self, request):
        return False


class VehicleAdmin(admin.ModelAdmin):
    list_display = ('owner', 'name', 'vehicle_type', 'plate_number', 'color', 'capacity')
    list_filter = ('vehicle_type',)
    readonly_fields = ('owner',)
    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('owner',),
        }),
        ('Details', {
            'classes': ('wide',),
            'fields': ('name', 'vehicle_type', 'plate_number', 'color', 'capacity',),

        }),
    )
    search_fields = ('vehicle_type', 'color',)
    ordering = ('name',)

    def has_add_permission(self, request):
        return False


class RequestAdmin(admin.ModelAdmin):
    list_display = ('passenger', 'driver', 'city', 'time', 'request_vehicle_type')
    list_filter = ('city', 'request_vehicle_type', 'passenger', 'driver',)
    readonly_fields = ('passenger', )
    fieldsets = (
        ('Users', {
            'classes': ('wide',),
            'fields': ('passenger', 'driver',),
        }),
        ('Details', {
            'classes': ('wide',),
            'fields': ('request_vehicle_type', 'city', 'time',),

        }),
    )
    search_fields = ('city', 'request_vehicle_type', 'passenger', 'driver',)
    ordering = ('passenger',)

    def has_add_permission(self, request):
        return False


class RideAdmin(admin.ModelAdmin):
    list_display = ('request', 'status', 'price', 'payment_status', 'payment_method')
    list_filter = ('payment_method', 'status')
    readonly_fields = ('request', 'status', 'price', 'payment_status', 'payment_method')
    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('request',),
        }),
        ('Details', {
            'classes': ('wide',),
            'fields': ('status', 'price', 'payment_status', 'payment_method',),
        }),
    )
    search_fields = ('status', 'payment_method',)
    ordering = ('status',)

    def has_add_permission(self, request):
        return False


class OrderAdmin(admin.ModelAdmin):
    list_display = ('request', 'slug')
    filter_horizontal = ('driver',)
    exclude = ('time_posted',)
    readonly_fields = ('request', 'slug')
    fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('request',),
        }),
        ('Drivers', {
            'classes': ('collapse',),
            'fields': ('driver',)
        }),
        ('Details', {
            'classes': ('wide',),
            'fields': ('slug',),

        }),
    )
    search_fields = ('passenger', 'driver',)
    ordering = ('time_posted',)

    def has_add_permission(self, request):
        return False


admin.site.register(User, UserAdmin)
admin.site.register(Driver, DriverAdmin)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(Request, RequestAdmin)
admin.site.register(Ride, RideAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.unregister(Group)

admin.site.site_header = "Dot360s Admin"