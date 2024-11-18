from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name', 'is_landlord', 'date_joined', 'is_active', 'is_staff')
    list_display_links = ('id', 'username', 'first_name')
    search_fields = ('id', 'username', 'first_name', 'last_name',)
    list_editable = ('is_active',)
    list_filter = ('is_active', 'date_joined', 'is_staff')
    fieldsets = ((None, {"fields": ("first_name", "last_name", "email", "password")}),
                 ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),)
    ordering = ("-date_joined",)


admin.site.register(User, UserAdmin)
