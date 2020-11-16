from django.contrib import admin
from main.models import Request, Ride, Order, Withdrawal
from django.contrib import messages 


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


class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'status', 'date',)
    exclude = ('date',)
    fieldsets = (
        ('Personal Details', {
            'classes': ('wide',),
            'fields': ('user', 'name'),
        }),
        ('Account Details', {
            'classes': ('wide',),
            'fields': ('amount', 'account_no','bank',)
        }),
        ('other', {
            'classes': ('wide',),
            'fields': ('reason', 'status'),

        }),
    )
    search_fields = ('name', 'date', 'status')
    ordering = ('date',)

    def pending_withdrawal(modelAdmin, request, queryset):
        if request.path == "/admin/main/withdrawal/":
            queryset.update(status = "pending")
        else:
            messages(request, messages.ERROR, "Oga, no dey try deadly things. go to the withdrawal model and do this stuff")


    def cancel_withdrawal(modelAdmin, request, queryset):
        if request.path == "/admin/main/withdrawal/":
            queryset.update(status = "cancelled")
        else:
            messages(request, messages.ERROR, "Oga, no dey try deadly things. go to the withdrawal model and do this stuff")

    def confirm_withdrawal(modelAdmin, request, queryset):
        if request.path == "/admin/main/withdrawal/":
            queryset.update(status = "completed")
            for obj in queryset:
                if obj.amount <= obj.user.account_balance:
                    obj.user.account_balance -= obj.amount 
                    obj.user.save()
                else: 
                    messages(request, messages.ERROR, "Withdrawal amount is_less than the user's account balance")
        else:
            messages(request, messages.ERROR, "Oga, no dey try deadly things. go to the withdrawal model and do this stuff")

    admin.site.add_action(pending_withdrawal, "Set withdrawal as pending")
    admin.site.add_action(cancel_withdrawal, "Cancel Withdrawal")
    admin.site.add_action(confirm_withdrawal, "Confirm Withdrawal")
    


admin.site.register(Request, RequestAdmin)
admin.site.register(Ride, RideAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Withdrawal, WithdrawalAdmin)