from django.db import models
from django.utils import timezone
from django.apps import apps
import random
import string
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Q




# Branch Model
class Branch(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

# Area Model
class Area(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True, null=True, unique=True)

    def __str__(self):
        return self.name

# Customer Model (Vendor)
class Customer(models.Model):
    vendor_name = models.CharField(max_length=200)
    vendor_address = models.TextField()
    vendor_phone = models.CharField(max_length=15)
    vendor_alt_phone = models.CharField(max_length=15, blank=True, null=True)

    created_by = models.ForeignKey('userapp.CourierUser', on_delete=models.CASCADE)

    def __str__(self):
        return self.vendor_name


class Courier(models.Model):
    # Order details
    created_by = models.ForeignKey('userapp.CourierUser', on_delete=models.CASCADE)
    tracking_id = models.CharField(max_length=50, unique=True, blank=True)
    destination = models.ForeignKey('courierapp.Branch', on_delete=models.CASCADE)
    order_type = models.CharField(max_length=50)
    delivery_type = models.CharField(max_length=50)
    order_date = models.DateTimeField(auto_now=True)
    package_name = models.CharField(max_length=100)
    weight = models.CharField(max_length=50)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    reference = models.CharField(max_length=50, blank=True, null=True)
    instruction = models.CharField(max_length=100, blank=True, null=True)

    # Vendor/Sender details
    vendor_name = models.ForeignKey('Customer', on_delete=models.CASCADE)

    # Customer details
    customer_name = models.CharField(max_length=200)
    customer_address = models.TextField()
    customer_phone = models.CharField(max_length=15)
    customer_alt_phone = models.CharField(max_length=15, blank=True, null=True)

    # COD (Cash on Delivery) details
    cod_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Generate tracking ID
    def generate_tracking_id(self):
        characters = string.ascii_uppercase + string.digits  # Uppercase letters + digits
        tracking_id = ''.join(random.choices(characters, k=10))  # Random 10-character ID
        return tracking_id

    def save(self, *args, **kwargs):
        """Override save method to auto-generate tracking_id if not provided"""
        if not self.tracking_id:
            self.tracking_id = self.generate_tracking_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.tracking_id

    @property
    def latest_status(self):
        # Return the latest status based on the timestamp
        return self.statuses.order_by('-timestamp').first()  # Using `order_by` to get the latest one
    

     # Method to get all couriers
    @staticmethod
    def get_all_couriers():
        return Courier.objects.all()

    # Method to get delivered couriers
    @staticmethod
    def get_delivered_couriers():
        return Courier.objects.filter(
            statuses__status='Delivered'
        ).distinct()

    # Method to get pending couriers (those not delivered)
    @staticmethod
    def get_pending_couriers():
        return Courier.objects.filter(
            ~Q(statuses__status='Delivered')  # Exclude those with "Delivered" status
        ).distinct()

    # Your other Courier model methods




class CourierStatus(models.Model):
    courier = models.ForeignKey('Courier', related_name='statuses', on_delete=models.CASCADE)
    updated_by = models.ForeignKey('userapp.CourierUser', on_delete=models.CASCADE)
    location_branch = models.ForeignKey('courierapp.Branch', on_delete=models.CASCADE)
    
    STATUS_CHOICES = [
        ('Booked by', 'Booked by'),
        ('Cancel', 'Cancel'),
        ('Packed for', 'Packed for'),
        ('Received by', 'Received by'),
        ('Sent to', 'Sent to'),
        ('In destination', 'In destination'),
        ('Out for delivery', 'Out for delivery'),
        ('Delivered', 'Delivered'),
    ]
    
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    timestamp = models.DateTimeField(default=timezone.now)  # Time when status was updated
    additional_info = models.TextField(blank=True, null=True)  # Optional extra info for each status update

    def __str__(self):
        return f"Status: {self.status} for Order {self.courier.tracking_id} at {self.timestamp}"

    class Meta:
        ordering = ['timestamp']  # Ensuring statuses are listed in chronological order for each courier




# Signal to create initial "Booked by" status when a new Courier is created
@receiver(post_save, sender=Courier)
def create_initial_status(sender, instance, created, **kwargs):
    if created:
        if not instance.created_by or not instance.vendor_name:
            raise ValueError("Courier must have a user and vendor_name to create an initial status.")
        
        try:
            CourierStatus.objects.create(
                courier=instance,
                status='Booked by',
                updated_by=instance.created_by,  # Use the correct user who created the courier
                location_branch=instance.vendor_name.branch_set.first(),  # Using first associated branch
            )
        except Exception as e:
            pass  # Handle or log the error as needed


class CourierPOD(models.Model):
    courier = models.ForeignKey('Courier', related_name='pods', on_delete=models.CASCADE)
    updated_by = models.ForeignKey('userapp.CourierUser', on_delete=models.CASCADE)
    pod_image = models.ImageField(upload_to='courier_pods/', blank=True, null=True)
