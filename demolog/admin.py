from django.contrib import admin
from .models import *
from django.utils.html import format_html
from django.core.exceptions import FieldError
from django.db import models
from django import forms


class UserAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone', 'name', 'address', 'city', 'you_are', 'members',
                    'joined_date', 'last_login', 'is_active', 'is_superuser')
    # ordering = ['id']
    list_filter = ('city', 'address', 'you_are', 'is_superuser')
    list_display_links = ('id', 'phone')
    readonly_fields = ('password', 'joined_date', 'last_login')
    search_fields = ('phone', 'name', 'address', 'city', 'you_are')


class PackageChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.plan} - {obj.type}" # type: ignore


class DashboardAdminForm(forms.ModelForm):
    current_plan = PackageChoiceField(queryset=Package.objects.all(), required=False)

    class Meta:
        model = Dashboard
        fields = '__all__'


class DashboardAdmin(admin.ModelAdmin):
    form = DashboardAdminForm
    list_display = ('id', 'name', 'service_id', 'thumbnail', 'get_current_plan', 'balance', 'reduce_balance', 'flexibility', 'flexibility_used')
    list_display_links = ('id', 'name', 'service_id')
    search_fields = ('name', 'service_id')
    readonly_fields = ('flexibility_used',)

    def get_current_plan(self, obj):
        if obj.current_plan:
            return f"{obj.current_plan.plan} - {obj.current_plan.type}"
        else:
            return None
    get_current_plan.short_description = 'Current Plan'

    def thumbnail(self, object):
        if object.image:
            return format_html('<img src="{}" width="30" style="border-radius:50%;">'.format(object.image.url))

    thumbnail.short_description = 'Profile Picture'


class PackageAdmin(admin.ModelAdmin):
    list_display = ('id', 'plan', 'type', 'per_meal', 'total_meals', 'total_amount')
    ordering = ('id',)
    list_display_links = ('id', 'plan')


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'payment_method', 'sender_number', 'transaction_id', 'plan', 'type', 'total_amount',
                    'started_date',
                    'expire_date', 'status', 'confirmed')
    ordering = ('status',)
    list_filter = ('payment_method', 'plan', 'type')
    list_display_links = ('id', 'user')

    

    # custom search_fields
    def get_search_fields(self, request):
        all_fields = [field.name for field in Payment._meta.get_fields() if isinstance(field, models.CharField)]
        return all_fields

    def get_search_results(self, request, queryset, search_term):
        try:
            self.search_fields = self.get_search_fields(request)
            return super().get_search_results(request, queryset, search_term)
        except FieldError as e:
            self.message_user(request, f"Invalid field name in search_fields: {str(e)}", level='ERROR')
            return queryset.none()

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        if request.GET.get('q') and response.context_data['cl'].result_count == 0:
            self.message_user(request, "No matching records found.", level='INFO')
        return response


class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'email', 'date_and_time', 'country', 'address', 'people', 'message')
    list_display_links = ('id', 'name', 'phone')
    search_fields = ('name', 'phone')


class ChefAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'Email', 'country', 'city', 'Address', 'people_you_can_serve')
    list_display_links = ('id', 'name', 'phone')
    search_fields = ('id', 'name', 'phone', 'Email', 'country', 'city', 'Address')
    
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email_or_phone', 'complaint_reason', 'complaint', 'submitted_at')


admin.site.register(UserAccount, UserAccountAdmin)
admin.site.register(Dashboard, DashboardAdmin)
admin.site.register(Package, PackageAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(ChefRegistraton, ChefAdmin)
admin.site.register(Feedback, FeedbackAdmin)
admin.site.register(MealOff)
