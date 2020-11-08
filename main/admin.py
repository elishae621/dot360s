from django.contrib import admin
from main.models import Request, Ride, Order


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


admin.site.register(Request, RequestAdmin)
admin.site.register(Ride, RideAdmin)
admin.site.register(Order, OrderAdmin)
