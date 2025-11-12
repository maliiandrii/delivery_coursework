from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


class UserRegistrationForm(UserCreationForm):
    """Form for user registration with additional fields"""

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Email'
        })
    )

    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Phone (optional)'
        })
    )

    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'placeholder': 'Delivery Address (optional)',
            'rows': 3
        })
    )

    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        initial='customer',
        widget=forms.Select(attrs={'class': 'form-input'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'address', 'user_type', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Username'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Confirm Password'
        })


class UserLoginForm(AuthenticationForm):
    """Custom login form with styled inputs"""

    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password'
        })
    )


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile"""

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'address']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }
