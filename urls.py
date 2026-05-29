from django.urls import path
from . import views

urlpatterns = [
    path('', views.live_feed, name='live_feed'),
    path('create/', views.create_listing, name='create_listing'),
    path('my/', views.my_listings, name='my_listings'),
    path('history/', views.donation_history, name='donation_history'),
    path('<int:pk>/', views.listing_detail, name='listing_detail'),
    path('<int:pk>/edit/', views.edit_listing, name='edit_listing'),
    path('<int:pk>/delete/', views.delete_listing, name='delete_listing'),
    path('<int:pk>/claim/', views.claim_listing, name='claim_listing'),
    path('claim/<int:pk>/complete/', views.complete_claim, name='complete_claim'),
    path('claim/<int:pk>/cancel/', views.cancel_claim, name='cancel_claim'),
]
