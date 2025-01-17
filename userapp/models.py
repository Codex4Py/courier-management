# CourierUser Model (User for Courier Management)
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from courierapp.models import Branch

class CourierUserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, username, password, **extra_fields)

class CourierUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    working_area = models.CharField(max_length=100)
    branch_name = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True)
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)  # Required for admin
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CourierUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'full_name']

    def __str__(self):
        return self.username