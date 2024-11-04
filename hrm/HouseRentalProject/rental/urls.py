from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf.urls.static import static
from django.conf import settings
from .views import process_payment
from .views import cancel_booking

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('login/', views.login_view, name='login'),  # User login
    path('register/', views.register_view, name='register'),  # User registration
    path('contact/', views.contact_view, name='contact'),  # Contact page
    path('dashboard/', views.user_dashboard, name='user_dashboard'),  # User dashboard
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),  # Admin dashboard
    path('property/add/', views.add_property, name='add_property'), 
    path('property/edit/<int:id>/', views.edit_property, name='edit_property'),  # Edit property
    path('property/delete/<int:id>/', views.delete_property, name='delete_property'),  # Delete property
    path('property/<int:id>/', views.view_property, name='view_property'),  # View property
    path('booking/<int:property_id>/', views.book_property, name='book_property'),  # Book property
    path('booking/cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('pg_accommodation/', views.pg_accommodation, name='pg_accommodation'),  # PG accommodations
    path('properties/', views.property_list, name='property_list'),  # Adjusted to use the correct view
    path('logout/', auth_views.LogoutView.as_view(), name='logout'), 
    path('cancel_booking/<int:booking_id>/', cancel_booking, name='cancel_booking'),
    path('admin_login/', views.admin_login, name='admin_login'),  # Admin login URL
    path('property/<int:property_id>/add-review/', views.add_review, name='add_review'),  # Add review
    path('property/view/<int:id>/', views.view_property, name='view_property'),
    path('property/detail/<int:id>/', views.property_detail, name='property_detail'),  # Property detail
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('search/', views.property_search, name='property_search'),
    path('property/<int:property_id>/payment/', views.create_payment, name='create_payment'),  # Payment URL updated
    path('booking/success/', views.booking_success, name='booking_success'),  # Booking success URL updated
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
