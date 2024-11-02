from django.contrib import admin
from booking_project.placement_models.models.apartments import Apartments
from booking_project.placement_models.models.categories import Categories


class ApartmentsAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'owner', 'created_at', 'is_active')
    list_display_links = ('id', 'title')
    search_fields = ('title', 'description')
    list_editable = ('is_active',)
    list_filter = ('is_active', 'created_at')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


admin.site.register(Categories, CategoryAdmin)
admin.site.register(Apartments, ApartmentsAdmin)
