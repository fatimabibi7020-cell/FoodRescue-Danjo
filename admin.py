from django.contrib import admin
from .models import FoodListing, Claim

@admin.register(FoodListing)
class FoodListingAdmin(admin.ModelAdmin):
    list_display = ['food_name','donor','category','quantity_servings','status','created_at']
    list_filter = ['status','category']

@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ['listing','ngo','status','claimed_at']
    list_filter = ['status']
