from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError


# models.py

class CustomUser(AbstractUser):
    phone_number = models.CharField(
        max_length=15, 
        blank=True, 
        null=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', message="Enter a valid phone number.")]
    )
    address = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Custom User'
        verbose_name_plural = 'Custom Users'
        # Remove `unique_together` and use `constraints` instead
        constraints = [
            models.UniqueConstraint(fields=['username', 'email'], name='unique_username_email')
        ]

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text='The groups this user belongs to.',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='custom_user',
    )

    def __str__(self):
        return self.username


# Facility model
class Facility(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Property(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()  # Keeping 'description' instead of 'summary'
    location = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Using 'price' instead of 'cost'
    is_pg = models.BooleanField(default=False)
    facilities = models.ManyToManyField(Facility, blank=True)
    address = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='property_images/', blank=True, null=True)  # Image field
    test_field = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.title



class Booking(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('pending', 'Pending'),
        ('canceled', 'Canceled'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')  # Default to pending for new bookings

    def __str__(self):
        return f"Booking for '{self.property.title}' by {self.user.username} from {self.start_date} to {self.end_date}"

    # Optional: Method to change booking status
    def update_status(self, new_status):
        if new_status in dict(self.STATUS_CHOICES).keys():
            self.status = new_status
            self.save()

# PG Facility model with verbose names
class PGFacility(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="pg_facilities")
    has_food = models.BooleanField(default=False, verbose_name="Food Availability")
    has_wifi = models.BooleanField(default=False, verbose_name="Wi-Fi Availability")
    additional_facility = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Facilities for {self.property.title}"


# Review model with rating validators and unique together constraint
class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating must be between 1 and 5"
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'property')

    def __str__(self):
        return f'Review by {self.user.username} for {self.property.title}'
class PropertyRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    property = models.ForeignKey('Property', on_delete=models.CASCADE)
    request_date = models.DateField(auto_now_add=True)  # Correctly separated line
    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Approved', 'Approved'),
            ('Rejected', 'Rejected')
        ],
        default='Pending'
    )

    def __str__(self):
        return f"Request by {self.user} for {self.property}"