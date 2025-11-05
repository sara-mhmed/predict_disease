from django.contrib import admin

from .models import GeneralTestResult
admin.site.register(GeneralTestResult)

class GeneralTestResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'predicted_disorder', 'created_at')
    search_fields = ('user__username', 'predicted_disorder')
    list_filter = ('created_at',)

def module_permissions(self, request):
    return request.user.is_superuser

def view_module(self, request):
    return request.user.is_superuser

def has_add_permission(self, request):
    return request.user.is_superuser

def has_change_permission(self, request, obj=None):
    return request.user.is_superuser

def has_delete_permission(self, request, obj=None):
    return request.user.is_superuser

# Register your models here.
