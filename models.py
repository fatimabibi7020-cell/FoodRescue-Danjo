from django.db import models
from django.utils import timezone
from accounts.models import CustomUser


class FoodListing(models.Model):
    CATEGORY = [
        ('cooked', 'Cooked'),
        ('packaged', 'Packaged'),
        ('raw', 'Raw'),
        ('bakery', 'Bakery'),
    ]
    STATUS = [
        ('active', 'Active'),
        ('claimed', 'Claimed'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
    ]

    donor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='listings')
    food_name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY)
    quantity_servings = models.PositiveIntegerField()
    quantity_kg = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)
    pickup_address = models.CharField(max_length=300)
    pickup_from = models.DateTimeField()
    pickup_by = models.DateTimeField()
    photo = models.ImageField(upload_to='listings/', null=True, blank=True)
    status = models.CharField(max_length=15, choices=STATUS, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.food_name} — {self.donor.business_name}'

    @property
    def donor_name(self):
        return self.donor.business_name or self.donor.full_name

    def is_expired(self):
        return timezone.now() > self.pickup_by

    def auto_expire(self):
        if self.status == 'active' and self.is_expired():
            self.status = 'expired'
            self.save()

    def time_ago(self):
        diff = timezone.now() - self.created_at
        mins = int(diff.total_seconds() / 60)
        if mins < 60:
            return f'{mins}m ago'
        hours = mins // 60
        if hours < 24:
            return f'{hours}h ago'
        return f'{diff.days}d ago'


class Claim(models.Model):
    STATUS = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    listing = models.OneToOneField(FoodListing, on_delete=models.CASCADE, related_name='claim')
    ngo = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='claims')
    pickup_time = models.DateTimeField(null=True, blank=True)
    contact_number = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=STATUS, default='active')
    claimed_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-claimed_at']

    def __str__(self):
        return f'{self.ngo.business_name} → {self.listing.food_name}'

    def mark_completed(self):
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
        self.listing.status = 'completed'
        self.listing.save()
