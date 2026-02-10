# from django.contrib import admin
#
# from properties.models.user import User
# from properties.models.review import Review
# from properties.models.location import Location
# from properties.models.property import Property
# from properties.models.property_details import PropertyDetails
# from properties.models.booking import Booking
#
# admin.site.register(Booking)
#
#
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('id', 'username', 'first_name', 'last_name', 'is_landlord', 'date_joined', 'is_active', 'is_staff')
#     list_display_links = ('id', 'username', 'first_name')
#     search_fields = ('id', 'username', 'first_name', 'last_name',)
#     list_editable = ('is_active',)
#     list_filter = ('is_active', 'date_joined', 'is_staff')
#     fieldsets = ((None, {'fields': ('first_name', 'last_name', 'email', 'password')}),
#                  ('Permissions', {'fields': ('is_staff', 'is_active', 'groups', 'user_permissions')}),)
#     ordering = ("-date_joined",)
#
#
# admin.site.register(User, UserAdmin)
#
# admin.site.register(Review)
#
#
# class PropertyAdmin(admin.ModelAdmin):
#     list_display = ('id', 'title', 'owner', 'created_at', 'is_active')
#     list_display_links = ('id', 'title')
#     search_fields = ('title', 'description')
#     list_editable = ('is_active',)
#     list_filter = ('is_active', 'created_at')
#
#
# admin.site.register(Property, PropertyAdmin)
# admin.site.register(PropertyDetails)
# admin.site.register(Location)
