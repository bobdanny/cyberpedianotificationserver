from django import forms

class SignUpForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        help_text='',
        widget=forms.TextInput(attrs={'placeholder': 'Username'})
    )
    email = forms.EmailField(
        help_text='',
        widget=forms.EmailInput(attrs={'placeholder': 'Email address'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'}),
        help_text='',
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}),
        help_text='',
    )
    is_active = forms.BooleanField(required=False, initial=True, help_text='')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = None  # Remove help text
            field.error_messages = {}  # Optionally clear error messages
