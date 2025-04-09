from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Reservation

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, max_length=30)
    last_name = forms.CharField(required=True, max_length=30)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['num_seats']
        widgets = {
            'num_seats': forms.NumberInput(attrs={'min': 1, 'max': 10})
        }
    
    def clean_num_seats(self):
        num_seats = self.cleaned_data.get('num_seats')
        if num_seats < 1:
            raise forms.ValidationError("Debe reservar al menos un asiento.")
        return num_seats

class MovieSearchForm(forms.Form):
    query = forms.CharField(
        max_length=100, 
        required=False, 
        widget=forms.TextInput(attrs={'placeholder': 'Buscar películas...'})
    )