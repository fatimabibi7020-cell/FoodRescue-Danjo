from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import FoodListing, Claim
from .forms import FoodListingForm, ClaimForm
from accounts.models import CustomUser, Notification
from accounts.views import push_notif


def expire_listings():
    FoodListing.objects.filter(status='active', pickup_by__lt=timezone.now()).update(status='expired')


@login_required
def create_listing(request):
    if not request.user.is_donor():
        return redirect('dashboard')
    if FoodListing.objects.filter(donor=request.user, status='active').count() >= 10:
        messages.error(request, 'Maximum 10 active listings allowed at once.')
        return redirect('dashboard')
    form = FoodListingForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        listing = form.save(commit=False)
        listing.donor = request.user
        listing.save()
        for ngo in CustomUser.objects.filter(role='ngo', status='approved'):
            push_notif(ngo, 'new_listing',
                       f'New listing: {listing.food_name}',
                       f'{listing.donor_name} posted {listing.food_name} ({listing.quantity_servings} servings) in {listing.pickup_address}.',
                       link=f'/listings/{listing.id}/')
        messages.success(request, f'Listing posted! NGOs have been notified.')
        return redirect('dashboard')
    unread = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return render(request, 'listings/create_listing.html', {'form': form, 'editing': False, 'unread': unread})


@login_required
def edit_listing(request, pk):
    listing = get_object_or_404(FoodListing, id=pk, donor=request.user)
    if listing.status != 'active':
        messages.error(request, 'Only active listings can be edited.')
        return redirect('my_listings')
    form = FoodListingForm(request.POST or None, request.FILES or None, instance=listing)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Listing updated.')
        return redirect('my_listings')
    unread = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return render(request, 'listings/create_listing.html', {'form': form, 'editing': True, 'listing': listing, 'unread': unread})


@login_required
def delete_listing(request, pk):
    listing = get_object_or_404(FoodListing, id=pk, donor=request.user)
    if listing.status != 'active':
        messages.error(request, 'Cannot delete a claimed listing.')
        return redirect('my_listings')
    listing.delete()
    messages.success(request, 'Listing deleted.')
    return redirect('my_listings')


@login_required
def my_listings(request):
    if not request.user.is_donor():
        return redirect('dashboard')
    listings = FoodListing.objects.filter(donor=request.user)
    unread = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return render(request, 'listings/my_listings.html', {'listings': listings, 'unread': unread})


@login_required
def donation_history(request):
    if not request.user.is_donor():
        return redirect('dashboard')
    listings = FoodListing.objects.filter(donor=request.user)
    unread = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return render(request, 'listings/donation_history.html', {'listings': listings, 'unread': unread})


@login_required
def live_feed(request):
    if not (request.user.is_ngo() and request.user.is_approved()):
        messages.error(request, 'Only approved NGOs can view the feed.')
        return redirect('dashboard')
    expire_listings()

    # seed dummy listings if none exist so NGO can test filters
    if not FoodListing.objects.filter(status='active').exists():
        _seed_dummy_listings()

    listings = FoodListing.objects.filter(status='active').select_related('donor')

    selected_cats = request.GET.getlist('category')
    area = request.GET.get('area', '')
    sort = request.GET.get('sort', 'newest')

    if selected_cats:
        listings = listings.filter(category__in=selected_cats)
    if area:
        listings = listings.filter(pickup_address__icontains=area)
    if sort == 'oldest':
        listings = listings.order_by('created_at')
    else:
        listings = listings.order_by('-created_at')

    meals_today = FoodListing.objects.filter(
        status='completed',
        updated_at__date=timezone.now().date()
    ).count() * 20

    unread = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return render(request, 'listings/live_feed.html', {
        'listings': listings,
        'selected_cats': selected_cats,
        'area': area, 'sort': sort,
        'meals_today': meals_today,
        'unread': unread,
    })


def _seed_dummy_listings():
    """Create sample listings so NGO can demo filters."""
    from django.utils import timezone
    import datetime
    dummy_donor = CustomUser.objects.filter(role='donor', status='approved').first()
    if not dummy_donor:
        return
    samples = [
        ('Fresh Biryani (Large Portion)', 'cooked', 50, 'F-7 Markaz, Islamabad', 'Freshly prepared chicken biryani, suitable for 20-25 people'),
        ('Assorted Fresh Bread & Pastries', 'bakery', 80, 'F-7 Markaz, Islamabad', 'Assorted breads and pastries from today'),
        ('Buffet Leftover — Mixed Items', 'packaged', 30, 'G-9, Islamabad', 'Mixed buffet items in sealed containers'),
        ('Fresh Vegetables & Fruits', 'raw', 40, 'G-6, Islamabad', 'Fresh seasonal vegetables and fruits'),
        ('Chicken Karahi & Naan', 'cooked', 25, 'F-10, Islamabad', 'Freshly cooked chicken karahi with naan'),
    ]
    now = timezone.now()
    for name, cat, qty, addr, desc in samples:
        FoodListing.objects.create(
            donor=dummy_donor,
            food_name=name, category=cat,
            quantity_servings=qty, pickup_address=addr,
            description=desc,
            pickup_from=now,
            pickup_by=now + datetime.timedelta(hours=3),
            status='active'
        )


@login_required
def listing_detail(request, pk):
    listing = get_object_or_404(FoodListing, id=pk)
    listing.auto_expire()
    can_claim = (
        request.user.is_ngo() and request.user.is_approved()
        and listing.status == 'active'
        and Claim.objects.filter(ngo=request.user, status='active').count() < 5
    )
    unread = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return render(request, 'listings/listing_detail.html', {
        'listing': listing, 'can_claim': can_claim, 'unread': unread
    })


@login_required
def claim_listing(request, pk):
    if not (request.user.is_ngo() and request.user.is_approved()):
        return redirect('dashboard')
    listing = get_object_or_404(FoodListing, id=pk)
    if listing.status != 'active':
        messages.error(request, 'This listing is no longer available.')
        return redirect('live_feed')
    if listing.is_expired():
        listing.status = 'expired'; listing.save()
        messages.error(request, 'This listing has just expired.')
        return redirect('live_feed')
    if Claim.objects.filter(ngo=request.user, status='active').count() >= 5:
        messages.error(request, 'You have 5 active claims. Complete one first.')
        return redirect('live_feed')
    form = ClaimForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        claim = form.save(commit=False)
        claim.listing = listing
        claim.ngo = request.user
        claim.save()
        listing.status = 'claimed'; listing.save()
        push_notif(listing.donor, 'listing_claimed',
                   'Your listing was claimed!',
                   f'{request.user.business_name or request.user.full_name} claimed "{listing.food_name}".',
                   link=f'/listings/{listing.id}/')
        messages.success(request, f'You claimed "{listing.food_name}" successfully!')
        return redirect('dashboard')
    unread = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return render(request, 'listings/claim_form.html', {
        'form': form, 'listing': listing, 'unread': unread
    })


@login_required
def complete_claim(request, pk):
    claim = get_object_or_404(Claim, id=pk)
    if request.user != claim.ngo and not request.user.is_admin_user():
        return redirect('dashboard')
    claim.mark_completed()
    push_notif(claim.listing.donor, 'listing_claimed',
               'Pickup completed!',
               f'{claim.ngo.business_name or claim.ngo.full_name} completed pickup of "{claim.listing.food_name}". Thank you!')
    messages.success(request, 'Pickup marked as completed!')
    return redirect('my_claims')


@login_required
def cancel_claim(request, pk):
    claim = get_object_or_404(Claim, id=pk, ngo=request.user)
    if claim.pickup_time and (claim.pickup_time - timezone.now()).total_seconds() < 3600:
        messages.error(request, 'Cannot cancel within 1 hour of scheduled pickup.')
        return redirect('my_claims')
    claim.status = 'cancelled'; claim.save()
    claim.listing.status = 'active'; claim.listing.save()
    messages.success(request, 'Claim cancelled. Listing is available again.')
    return redirect('my_claims')
