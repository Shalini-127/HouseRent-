from django import forms
from django.contrib.auth.models import User
from .models import Property, Booking, Review, PGFacility
from .models import CustomUser
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
User = get_user_model()
class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['title', 'description', 'location', 'price', 'image']

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['start_date', 'end_date']
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        labels = {
            'rating': 'Rating (1-5)',
            'comment': 'Your Comment'
        }
        help_texts = {
            'rating': 'Please provide a rating between 1 and 5.',
            'comment': 'Share your experience with this property.',
        }
        widgets = {
            'rating': forms.NumberInput(attrs={
                'min': 1,
                'max': 5,
                'placeholder': '1-5',
                'class': 'form-control',
            }),
            'comment': forms.Textarea(attrs={
                'placeholder': 'Write your review here...',
                'rows': 4,
                'class': 'form-control',
            }),
        }

class PGFacilityForm(forms.ModelForm):
    class Meta:
        model = PGFacility
        fields = ['has_food', 'has_wifi', 'additional_facility']

        
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)  # Ensure email is included

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2') 

