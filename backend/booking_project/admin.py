from django.contrib import admin

from booking_project.models.user import User
from booking_project.models.review import Review
from booking_project.models.placement_location import Location
from booking_project.models.placement import Placement
from booking_project.models.category import Category
from booking_project.models.placement_details import PlacementDetails
from booking_project.models.booking_details import BookingDetails

admin.site.register(BookingDetails)


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

admin.site.register(Review)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class PlacementAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'owner', 'created_at', 'is_active')
    list_display_links = ('id', 'title')
    search_fields = ('title', 'description')
    list_editable = ('is_active',)
    list_filter = ('is_active', 'created_at')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Placement, PlacementAdmin)
admin.site.register(PlacementDetails)
admin.site.register(Location)
