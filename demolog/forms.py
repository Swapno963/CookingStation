from email.policy import default
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.core.exceptions import ValidationError


class UserRegisterForm(UserCreationForm):
    name = forms.CharField(max_length=30, label='', widget=forms.TextInput(attrs={'placeholder': 'Name'}))
    phone = forms.CharField(label='', max_length=15, widget=forms.NumberInput(attrs={'placeholder': "Phone number"}))
    email = forms.EmailField(max_length=50, label='', required=False, widget=forms.EmailInput(attrs={'placeholder': 'Email (Optional)'}))
    country = forms.ChoiceField(choices=UserAccount.COUNTRY_CHOICES, label='', widget=forms.Select(attrs={'placeholder': 'Country'}))
    city = forms.CharField(max_length=30, label='', widget=forms.TextInput(attrs={'placeholder': 'City'}))
    address = forms.CharField(max_length=150, label='', widget=forms.TextInput(attrs={'placeholder': 'Address'}))
    you_are = forms.ChoiceField(choices=UserAccount.YOU_ARE_CHOICES, label='', widget=forms.Select(attrs={'placeholder': 'You Are'}))
    members = forms.IntegerField(label='', required=False, widget=forms.NumberInput(attrs={'placeholder': 'Members'}))
    is_agreed = forms.BooleanField(label="Agree to terms and conditions")

    password1 = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    password2 = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))

    class Meta(UserCreationForm.Meta):
        model = UserAccount
        fields = ['name', 'phone', 'email', 'country', 'city', 'address', 'you_are', 'members']
        widgets = {
            'members': forms.HiddenInput(),  # Set widget to HiddenInput if you want it hidden initially
        }

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['members'].required = False

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.startswith('01') and len(phone) != 11:
            raise ValidationError("Phone number must start with '01' and be exactly 11 digits long")
        return phone
    
    def clean(self):
        cleaned_data = super().clean()
        you_are = cleaned_data.get('you_are')
        members = cleaned_data.get('members')

        if you_are != 'Family' or members == None:
            cleaned_data['members'] = 1

        return cleaned_data


class UserLoginForm(forms.Form):
    phone = forms.CharField(label='', max_length=15,
                            widget=forms.NumberInput(attrs={'placeholder': "Enter Phone number"}))
    password = forms.CharField(label='', widget=forms.PasswordInput(attrs={'placeholder': "Enter your password"}))


class EventForm(forms.ModelForm):
    people = forms.CharField(max_length=5, label="No of People")

    class Meta:
        model = Event
        fields = '__all__'
        widgets = {
            'date_and_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),

        }


class ChefRegistrationForm(forms.ModelForm):
    class Meta:
        model = ChefRegistraton
        fields = '__all__'
