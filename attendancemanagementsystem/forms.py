from django import forms
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

# Custom Password Change Form
class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(), label='Current Password'
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(), label='New Password'
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(), label='Confirm New Password'
    )

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(required=True, label="Full Name")
    email = forms.EmailField(required=True)

    DEPARTMENT_CHOICES = [
        ('cs', 'Computer Science'),
        ('mc', 'Mass Communication'),
        ('journalism', 'Journalism'),
        ('eee', 'Electrical Electronics Engineering'),
        ('ba', 'Business Administration'),
        ('se', 'Software Engineering'),
    ]

    LEVEL_CHOICES = [
        ('100', '100'),
        ('200', '200'),
        ('300', '300'),
        ('400', '400'),
    ]

    SEMESTER_CHOICES = [
        ('1st', '1st'),
        ('2nd', '2nd'),
    ]

    department = forms.ChoiceField(choices=DEPARTMENT_CHOICES, required=True)
    level = forms.ChoiceField(choices=LEVEL_CHOICES, required=True)
    semester = forms.ChoiceField(choices=SEMESTER_CHOICES, required=True)

    class Meta:
        model = CustomUser
        fields = ['full_name', 'email', 'password1', 'password2', 'department', 'level', 'semester']

    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already registered")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.full_name = self.cleaned_data['full_name']
        user.email = self.cleaned_data['email'].lower()
        user.department = self.cleaned_data['department']
        user.level = self.cleaned_data['level']
        user.semester = self.cleaned_data['semester']
        if commit:
            user.save()
        return user


# Custom Authentication Form (login)
class CustomAuthenticationForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            email = email.lower()
            try:
                user_obj = User.objects.get(email=email)
                # Since USERNAME_FIELD is 'email', pass email as username to authenticate
                user = authenticate(self.request, username=email, password=password)
            except User.DoesNotExist:
                user = None

            if user is None:
                raise forms.ValidationError(_("Invalid login credentials"))
            self.user = user

        return cleaned_data

    def get_user(self):
        return self.user





# forms.py
from django import forms
from .models import Course

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'code', 'department', 'level', 'semester', 'credit_units']






# forms.py

from django import forms
from .models import Apartment

from django import forms
from .models import Apartment

from django import forms
from .models import Apartment

from django import forms
from .models import Apartment

class ApartmentForm(forms.ModelForm):
    class Meta:
        model = Apartment
        fields = ['name', 'location', 'price', 'category', 'hot']
        labels = {
            'name': 'Apartment Name',
            'location': 'Location',
            'price': 'Price ($)',
            'category': 'Apartment Category',
            'hot': 'Mark as Hot Listing',
        }
        help_texts = {
            'price': 'Enter the price in USD.', 
            'category': 'Select the type of apartment.',
            'hot': 'Check if this apartment should be featured prominently.',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter apartment name'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter location'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'hot': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
