from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CourierUser

class CourierUserAdmin(UserAdmin):
    # Define the model to be used in the admin
    model = CourierUser

    # Fields to display in the admin list view
    list_display = ('email', 'username', 'full_name', 'phone_number', 'working_area', 'branch_name', 'is_staff', 'is_active', 'date_joined')

    # Fields that can be used to filter the list
    list_filter = ('is_staff', 'is_active', 'branch_name', 'date_joined')

    # Fields for search functionality
    search_fields = ('email', 'username', 'full_name')

    # Fields that can be clicked to edit
    ordering = ('-date_joined',)

    # Define the fields for the form in the admin
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('username', 'full_name', 'phone_number', 'working_area', 'branch_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Fieldsets for adding a new user (separate form for user creation)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'full_name', 'phone_number', 'working_area', 'branch_name', 'is_active', 'is_staff'),
        }),
    )

    # Allow modification of password from the admin interface
    add_permission = ('is_staff',)

    # Customize the save method (optional)
    def save_model(self, request, obj, form, change):
        if not change:
            obj.set_password(obj.password)  # Ensure password is hashed when saving
        obj.save()

# Register the CourierUser model with the custom admin configuration
admin.site.register(CourierUser, CourierUserAdmin)
