from django.contrib import admin
from user.models import (
    User, Driver, Vehicle
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
    readonly_fields = ('is_driver', 'is_staff')
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
        ('Referral Details', {
            'classes': ('wide',),
            'fields': ('referral', 'referral_status')
        })
    )
    search_fields = ('is_driver', 'is_staff',)
    ordering = ('firstname',)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(UserAdmin, self).get_inline_instances(request, obj)


    def driver(self, obj):
        return obj.is_driver == 1

    driver.boolean = True

    # make sure that make driver and not driver only works on drivers
    def make_driver(modelAdmin, request, queryset):
        if request.path == "/admin/user/user/":
            queryset.update(is_driver = 1)
            for obj in queryset:
                obj.save()
            messages.success(request, "Selected User(s) Marked as drivers Successfully !!")
        else:
            messages.error(request, "This can only be done from the user model")
    
    def make_not_driver(modelAdmin, request, queryset):
        if request.path == "/admin/user/user/":
            queryset.update(is_driver = 0)
            for obj in queryset:
                Driver.objects.filter(user=obj).delete()
                obj.save()
            messages.success(request, "Selected user(s) Marked as non drivers Successfully !!")
        else: 
            messages.error(request, "This can only be done from the user model")

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


admin.site.register(User, UserAdmin)
admin.site.register(Driver, DriverAdmin)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.unregister(Group)

admin.site.site_header = "Dot360s Admin"