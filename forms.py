from django import forms
from django.utils import timezone
from .models import FoodListing, Claim


class FoodListingForm(forms.ModelForm):
    class Meta:
        model = FoodListing
        fields = ['food_name', 'category', 'quantity_servings', 'quantity_kg',
                  'description', 'pickup_address', 'pickup_from', 'pickup_by', 'photo']
        widgets = {
            'food_name':        forms.TextInput(attrs={'placeholder': 'e.g. Biryani & Karahi', 'class': 'fr-input'}),
            'quantity_servings':forms.NumberInput(attrs={'placeholder': '50', 'class': 'fr-input'}),
            'quantity_kg':      forms.NumberInput(attrs={'placeholder': '10', 'class': 'fr-input'}),
            'description':      forms.Textarea(attrs={'placeholder': 'Allergens, storage notes...', 'rows': 3, 'class': 'fr-input'}),
            'pickup_address':   forms.TextInput(attrs={'placeholder': 'Blue Area, Islamabad', 'class': 'fr-input'}),
            'pickup_from':      forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'fr-input'}, format='%Y-%m-%dT%H:%M'),
            'pickup_by':        forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'fr-input'}, format='%Y-%m-%dT%H:%M'),
        }
        labels = {
            'food_name': 'Food Name',
            'quantity_servings': 'Quantity (servings)',
            'quantity_kg': 'Weight in kg (optional)',
            'pickup_from': 'Pickup From',
            'pickup_by': 'Pickup By',
            'photo': 'Food Photo (max 5MB)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            for f in ['pickup_from', 'pickup_by']:
                val = getattr(self.instance, f)
                if val:
                    self.initial[f] = val.strftime('%Y-%m-%dT%H:%M')

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo and hasattr(photo, 'size') and photo.size > 5 * 1024 * 1024:
            raise forms.ValidationError('Photo must be under 5MB.')
        return photo

    def clean(self):
        cd = super().clean()
        pf = cd.get('pickup_from')
        pb = cd.get('pickup_by')
        if pf and pb:
            if pf >= pb:
                raise forms.ValidationError('Pickup end time must be after start time.')
            if pb <= timezone.now():
                raise forms.ValidationError('Pickup window cannot be in the past.')
        return cd


class ClaimForm(forms.ModelForm):
    class Meta:
        model = Claim
        fields = ['pickup_time', 'contact_number', 'notes']
        widgets = {
            'pickup_time':    forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'fr-input'}, format='%Y-%m-%dT%H:%M'),
            'contact_number': forms.TextInput(attrs={'placeholder': '+92-300-1234567', 'class': 'fr-input'}),
            'notes':          forms.Textarea(attrs={'rows': 2, 'placeholder': 'Any special instructions...', 'class': 'fr-input'}),
        }
