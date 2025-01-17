from django.contrib import admin
from .models import Branch, Area, Customer, Courier, CourierStatus
from django.utils.translation import gettext_lazy as _

# Register Branch Model
@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Display branch name in the list view
    search_fields = ('name',)  # Enable search by branch name
    ordering = ('name',)  # Order by branch name

# Register Area Model
@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ('name', 'branch')  # Display area name and its branch in list view
    search_fields = ('name',)  # Enable search by area name
    list_filter = ('branch',)  # Filter by branch
    ordering = ('branch', 'name')  # Order by branch and then area name

# Register Customer Model
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('vendor_name', 'vendor_phone', 'vendor_alt_phone', 'created_by')
    search_fields = ('vendor_name', 'vendor_phone', 'vendor_address')
    list_filter = ('created_by',)  # Filter by the user who created the customer
    ordering = ('vendor_name',)

# Register Courier Model
@admin.register(Courier)
class CourierAdmin(admin.ModelAdmin):
    list_display = ('tracking_id', 'order_type', 'delivery_type', 'order_date', 'package_name', 'vendor_name', 'customer_name', 'total_amount', 'cod_amount')
    search_fields = ('tracking_id', 'package_name', 'order_type', 'delivery_type', 'vendor_name__vendor_name', 'customer_name')
    list_filter = ('order_type', 'delivery_type', 'created_by')  # Filter by order type, delivery type, and creator
    ordering = ('order_date',)

# Register CourierStatus Model
@admin.register(CourierStatus)
class CourierStatusAdmin(admin.ModelAdmin):
    list_display = ('courier', 'status', 'location_branch', 'timestamp', 'updated_by')
    search_fields = ('courier__tracking_id', 'status', 'location_branch__name', 'updated_by__username')
    list_filter = ('status', 'location_branch', 'updated_by')  # Filter by status, branch, and updated_by
    ordering = ('-timestamp',)  # Order by timestamp in descending order

    # Display choices in a more user-friendly way
    def status_display(self, obj):
        return dict(CourierStatus.STATUS_CHOICES).get(obj.status, _('Unknown Status'))
    status_display.short_description = _('Status')

