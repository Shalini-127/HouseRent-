from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.utils import timezone
from django.utils.timezone import now
from .models import Property, Booking, CustomUser
from django.contrib.auth.models import User
from .models import Property, Booking, Review, PGFacility, CustomUser
from .forms import PropertyForm, BookingForm, ReviewForm, PGFacilityForm, UserRegistrationForm
from django.contrib.auth.forms import AuthenticationForm  # Import AuthenticationForm
from django.urls import reverse
from .forms import ReviewForm
from django.core.exceptions import ValidationError
from .models import PropertyRequest
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import stripe
from .payment import calculate_amount


stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

@login_required
def home(request):
    # Get all properties with prefetch of related reviews
    properties = Property.objects.prefetch_related('reviews').all()
    
    # Get bookings for the logged-in user
    bookings = Booking.objects.filter(user=request.user)
    
    # Get the latest 5 reviews (adjust number as needed) and include related property
    recent_reviews = Review.objects.select_related('property').order_by('-created_at')[:5]

    return render(request, 'rental/home.html', {
        'properties': properties,
        'bookings': bookings,
        'recent_reviews': recent_reviews,
    })
@login_required
def user_dashboard(request):
    """Display the user dashboard with booking information, properties, reviews, and property requests."""

    # Get all bookings for the logged-in user
    bookings = Booking.objects.filter(user=request.user)

    # Get all properties owned by the logged-in user
    properties = Property.objects.filter(owner=request.user)

    # Fetch reviews related to the user's bookings
    reviews = Review.objects.filter(user=request.user).select_related('property')

    # Create a dictionary to track reviews by property
    user_reviews = {review.property.id: review for review in reviews}

    # Create a dictionary to track whether each booking has an existing review
    review_status = {booking.id: booking.property.id in user_reviews for booking in bookings}

    # Check for a POST request to submit a review
    if request.method == "POST":
        review_form = ReviewForm(request.POST)

        if review_form.is_valid():
            booking_id = request.POST.get("booking_id")
            booking = get_object_or_404(Booking, id=booking_id, user=request.user)

            # Check if a review already exists for this booking's property
            if booking.property.id not in user_reviews:
                review = review_form.save(commit=False)
                review.user = request.user
                review.property = booking.property

                try:
                    review.full_clean()  # Validate the model fields
                    review.save()
                    messages.success(request, 'Your review has been submitted successfully!')  # Success message
                except ValidationError as e:
                    review_form.add_error(None, e)
                    messages.error(request, 'There was an error submitting your review.')  # Error message

                return redirect('user_dashboard')  # Redirect to prevent duplicate submissions
        else:
            messages.error(request, 'Please correct the errors below.')  # Error message for form validation failures
    else:
        review_form = ReviewForm()

    # Fetch property requests for the logged-in user
    property_requests = PropertyRequest.objects.filter(user=request.user)

    # If there's a success message for booking confirmation
    if 'booking_confirmed' in request.session:
        messages.success(request, 'Payment was successful! Your booking is confirmed.')
        del request.session['booking_confirmed']  # Remove the message after displaying it

    # Prepare context for rendering the dashboard
    context = {
        'properties': properties,
        'bookings': bookings,
        'review_form': review_form,
        'review_status': review_status,  # Pass review status to template
        'user_reviews': user_reviews,  # Pass user reviews to template
        'property_requests': property_requests,  # Pass property requests to template
    }

    return render(request, 'rental/user_dashboard.html', context)

# def property_list(request):
#     properties = Property.objects.filter(is_pg=False)  # Retrieve properties that are not PG accommodations
#     return render(request, 'rental/property_list.html', {'properties': properties})  # Render the template with properties

def property_list(request):
    properties = Property.objects.all()
    return render(request, 'rental/property_list.html', {'properties': properties})

def pg_facilities_form(request):
    if request.method == 'POST':
        form = PGFacilityForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('student_dashboard')  # Ensure 'student_dashboard' is a defined URL
    else:
        form = PGFacilityForm()
    return render(request, 'rental/pg_facilities_form.html', {'form': form})

def login_view(request):
    # Redirect authenticated users directly to the dashboard
    if request.user.is_authenticated:
        return redirect('user_dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome, {username}!")
                return redirect('user_dashboard')  # Redirect to user dashboard after login
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()

    return render(request, 'rental/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()  # Save the new user
            return redirect('login')  # Redirect to the login page after successful registration
    else:
        form = UserRegistrationForm()

    return render(request, 'rental/register.html', {'form': form})  
def contact_view(request):
    if request.method == 'POST':
        # Handle the post request, e.g., save the data or send an email
        pass
    return render(request, 'rental/contact.html')

@login_required
def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)  # Accept files for image upload
        if form.is_valid():
            property_instance = form.save(commit=False)
            property_instance.owner = request.user  # Set the property owner to the logged-in user
            property_instance.save()
            messages.success(request, 'Property added successfully!')  # Success message
            return redirect('user_dashboard')  # Redirect to the user dashboard or property list
    else:
        form = PropertyForm()

    return render(request, 'rental/add_property.html', {'form': form})
    
@login_required
def edit_property(request, id):
    # Get the property instance or return a 404 if it doesn't exist
    property_instance = get_object_or_404(Property, id=id)

    if request.method == "POST":
        # Bind form to POST data and the existing instance
        form = PropertyForm(request.POST, instance=property_instance)
        if form.is_valid():
            # Save the updated property instance
            form.save()
            # Add a success message
            messages.success(request, 'Property updated successfully!')
            # Redirect to the view_property page
            return redirect('view_property', id=property_instance.id)
    else:
        # Initialize the form with the existing property instance
        form = PropertyForm(instance=property_instance)

    # Render the edit_property template with the form and property data
    return render(request, 'rental/edit_property.html', {'form': form, 'property': property_instance}) 
@login_required
def delete_property(request, id):
    property_instance = get_object_or_404(Property, id=id)
    
    if request.method == "POST":
        property_instance.delete()
        messages.success(request, 'Property deleted successfully!')
        return redirect('user_dashboard')  # Redirect to user dashboard or appropriate page
    
    return render(request, 'rental/property_confirm_delete.html', {'property': property_instance})

def view_property(request, id):
    property_instance = get_object_or_404(Property, id=id)
    return render(request, 'rental/property_detail.html', {'property': property_instance})


@login_required
def book_property(request, property_id):
    property = get_object_or_404(Property, id=property_id)

    # Check if the user has an existing booking for this property
    existing_booking = Booking.objects.filter(user=request.user, property=property).first()

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # Validate start_date and end_date
        if not start_date or not end_date:
            messages.error(request, "Please provide valid start and end dates.")
            return render(request, 'rental/property_detail.html', {
                'property': property,
                'booking': existing_booking,
            })

        try:
            # Convert start_date and end_date to datetime objects
            start_date_obj = timezone.datetime.fromisoformat(start_date)
            end_date_obj = timezone.datetime.fromisoformat(end_date)

            # Check if the end date is after the start date
            if end_date_obj <= start_date_obj:
                messages.error(request, "End date must be after the start date.")
                return render(request, 'rental/property_detail.html', {
                    'property': property,
                    'booking': existing_booking,
                })

            # Check if a booking already exists for this period
            if existing_booking:
                messages.warning(request, "You already have a booking for this property.")
                return redirect('user_dashboard')  # Redirect to the user dashboard or any other page
            
            # Assuming you have some payment processing logic here
            # (Add your payment logic here. If successful, proceed to create the booking.)

            # Create a new booking
            booking = Booking.objects.create(
                user=request.user,
                property=property,
                start_date=start_date_obj,
                end_date=end_date_obj,
                status='Confirmed'  # Set the booking status to confirmed
            )

            messages.success(request, "Your booking has been confirmed!")  # Success message
            return redirect('user_dashboard')  # Redirect to user dashboard or property details

        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD.")
            return render(request, 'rental/property_detail.html', {
                'property': property,
                'booking': existing_booking,
            })

    return render(request, 'rental/property_detail.html', {
        'property': property,
        'booking': existing_booking,  # Pass the existing booking object to the template
    })

# @login_required
# def cancel_booking(request, booking_id):
#     if request.method == 'POST':
#         booking = get_object_or_404(Booking, id=booking_id, user=request.user)  # Check user ownership
#         try:
#             booking.delete()
#             messages.success(request, 'Booking canceled successfully.')
#         except Exception as e:  # You can specify more specific exceptions as needed
#             messages.error(request, 'There was an error canceling your booking. Please try again.')
#     return redirect('user_dashboard')

def pg_accommodation(request):
    # Your view logic here
    return render(request, 'rental/pg_accommodation.html')

def admin_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        
        # Check if the user is authenticated and is a staff member
        if user is not None and user.is_staff:
            login(request, user)  # Log the user in
            return redirect(reverse('admin_dashboard'))  # Redirect to admin dashboard
        
        # If authentication fails
        error_message = "Invalid credentials or you are not authorized."
        return render(request, 'rental/admin_login.html', {'error': error_message})

    return render(request, 'rental/admin_login.html')

def property_detail(request, id):
    # Retrieve the property instance
    property_instance = get_object_or_404(Property, id=id)

    # Retrieve the booking for the logged-in user, if authenticated
    booking = property_instance.booking_set.filter(user=request.user).first() if request.user.is_authenticated else None

    # Pass both the property instance and the booking to the template
    context = {
        'property': property_instance,
        'booking': booking,
    }
    
    return render(request, 'rental/property_detail.html', context)

def add_review(request, property_id):
    property_instance = get_object_or_404(Property, id=property_id)
    
    # Check if the user has already reviewed this property
    existing_review = Review.objects.filter(property=property_instance, user=request.user).first()
    
    if request.method == 'POST':
        if existing_review:
            # Update the existing review
            form = ReviewForm(request.POST, instance=existing_review)
        else:
            # Create a new review if one doesn't exist
            form = ReviewForm(request.POST)

        if form.is_valid():
            review = form.save(commit=False)
            review.property = property_instance
            review.user = request.user
            review.save()
            action = "updated" if existing_review else "added"
            messages.success(request, f"Your review has been {action} successfully.")
            return redirect('property_detail', id=property_id)
        else:
            messages.error(request, "There was an error submitting your review.")
    else:
        # Initialize the form with the existing review if it exists, else a blank form
        form = ReviewForm(instance=existing_review) if existing_review else ReviewForm()

    return render(request, 'rental/property_detail.html', {'form': form, 'property': property_instance})
def admin_dashboard(request):
    User = get_user_model()

    # Get counts for display
    total_properties = Property.objects.count()  # Total properties
    total_bookings = Booking.objects.count()  # Total bookings
    total_users = User.objects.count()  # Total users
    canceled_bookings = Booking.objects.filter(status='Canceled').count()  # Total canceled bookings

    # Get properties booked by each user with related property details
    user_bookings = (
        Booking.objects
        .select_related('user', 'property')  # Optimize the query to include user and property details
        .filter(status='confirmed')  # Filter by confirmed status
    )

    # Get the last login times for all users who have logged in at least once
    users_last_login = User.objects.filter(last_login__isnull=False).values('username', 'last_login')

    # Context dictionary to pass data to the template
    context = {
        'total_properties': total_properties,
        'total_bookings': total_bookings,
        'total_users': total_users,
        'canceled_bookings': canceled_bookings,
        'user_bookings': user_bookings,  # Pass the entire queryset instead of values
        'users_last_login': users_last_login,  # Last login times for users
    }

    return render(request, 'rental/admin_dashboard.html', context)
@login_required
def cancel_booking(request, booking_id):
    """Cancel a booking."""
    if request.method == 'POST':
        # Get the booking object, ensuring it belongs to the logged-in user
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
        try:
            booking.delete()  # Delete the booking
            messages.success(request, 'Booking canceled successfully.')
        except Exception as e:  # Handle potential exceptions
            messages.error(request, 'There was an error canceling your booking. Please try again.')
    
    return redirect('user_dashboard')  # Adjust the URL name as needed

@login_required
def cancel_property_request(request, request_id):
    """Cancel a property request."""
    property_request = get_object_or_404(PropertyRequest, id=request_id, user=request.user)
    property_request.status = 'Cancelled'
    property_request.save()
    messages.success(request, 'Property request canceled successfully.')  # Provide user feedback
    return redirect('rental/user_dashboard') 

def newsletter_subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        # Here you can add logic to save the email to a database or a mailing list
        messages.success(request, 'Thank you for subscribing to our newsletter!')
        return redirect(' ')  # Change this to the desired redirect URL
    return render(request, 'home.html')


def property_search(request):
    location = request.GET.get('location')
    properties = Property.objects.filter(location__icontains=location)  # Adjust field name as necessary
    return render(request, 'rental/property_list.html', {'properties': properties})

@csrf_exempt
def process_payment(request, property_id):
    if request.method == "POST":
        token = request.POST.get('stripeToken')

        try:
            # Charge the user's card
            charge = stripe.Charge.create(
                amount=1000,  # Amount in cents (adjust this based on your property price)
                currency='usd',
                description='Property Booking',
                source=token,
            )

            # Save payment details to the database and create a booking
            property_instance = get_object_or_404(Property, id=property_id)

            # Create a new booking associated with the logged-in user
            Booking.objects.create(
                user=request.user,
                property=property_instance,
                # Add any other necessary fields for the booking
            )

            return redirect('booking_success')  # Redirect to a success page

        except stripe.error.StripeError as e:
            # Handle payment failure
            return render(request, 'payment_failed.html', {'error': str(e)})  # Pass error message for display

    # If not a POST request, redirect back to the property details page
    return redirect('property_details', property_id=property_id)

@login_required
def create_payment(request, property_id):
    """Create a payment for a booking."""
    # Assume payment processing logic is here
    if request.method == 'POST':
        # Your payment processing logic goes here
        
        # If payment is successful
        payment_successful = True  # Replace with your actual payment processing logic

        if payment_successful:
            # Add a success message
            messages.success(request, 'Payment was successful! Your booking is confirmed.')
            return redirect('user_dashboard')  # Redirect to the user dashboard or any other page
        else:
            messages.error(request, 'There was an error processing your payment. Please try again.')

    # Render payment page or other logic as needed
    return render(request, 'rental/payment.html', {})

def create_booking(user, property_id):
    # Implement your logic to save the booking in the database
    pass

from datetime import date

def calculate_amount(property_id=None, start_date=None, end_date=None):
    if property_id is not None:
        # Implement logic to get the property price based on property_id
        property_price = 1000  # Example fixed price for demonstration
        return property_price

    if start_date is not None and end_date is not None:
        # Example logic to calculate total price based on date range
        property_price_per_night = 100  # Example price per night
        duration = (end_date - start_date).days
        if duration < 0:
            raise ValueError("End date must be after start date.")
        return duration * property_price_per_night

    raise ValueError("Either property_id or both start_date and end_date must be provided.")

# Example usage
# For calculating based on property ID
amount_by_id = calculate_amount(property_id=1)

# For calculating based on dates
start_date = date(2024, 11, 1)
end_date = date(2024, 11, 5)
amount_by_dates = calculate_amount(start_date=start_date, end_date=end_date)

print("Amount based on property ID:", amount_by_id)
print("Amount based on date range:", amount_by_dates)

def booking_success(request):
    return render(request, 'rental/booking_success.html')
