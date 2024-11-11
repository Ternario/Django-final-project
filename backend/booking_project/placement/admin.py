from django.contrib import admin
from booking_project.placement.models.placement import Placement
from booking_project.placement.models.categories import Categories
from booking_project.placement.models.placement_details import PlacementDetails


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class PlacementAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'owner', 'created_at', 'is_active')
    list_display_links = ('id', 'title')
    search_fields = ('title', 'description')
    list_editable = ('is_active',)
    list_filter = ('is_active', 'created_at')


admin.site.register(Categories, CategoryAdmin)
admin.site.register(Placement, PlacementAdmin)
