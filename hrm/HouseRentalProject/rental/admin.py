from django.contrib import admin
from .models import Property, CustomUser, Booking
from django.contrib.auth.admin import UserAdmin

# Inline admin for Booking model to show bookings related to Property and CustomUser
class BookingInline(admin.TabularInline):
    model = Booking
    extra = 0
    fields = ('property', 'start_date', 'end_date', 'status')  # Updated field names for clarity
    readonly_fields = ('property', 'start_date', 'end_date', 'status')  # Readonly fields

# Admin for Property model
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'price', 'is_pg', 'created_at')  # Fields to display
    search_fields = ('title', 'owner__username')  # Searchable fields
    list_filter = ('is_pg',)  # Filters for admin list view
    inlines = [BookingInline]  # Show bookings related to each property

admin.site.register(Property, PropertyAdmin)  # Register Property model with custom admin

# Admin for CustomUser model with UserAdmin customization
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'phone_number', 'address', 'is_staff', 'is_active')  # Displayed fields
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('phone_number', 'address')}),  # Additional fields for user creation
    )
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone_number', 'address')}),  # Additional fields for user editing
    )
    inlines = [BookingInline]  # Show bookings related to each user

admin.site.register(CustomUser, CustomUserAdmin)  # Register CustomUser model with custom admin
