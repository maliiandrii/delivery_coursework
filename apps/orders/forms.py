from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    """Form for creating a new order"""

    save_delivery_data = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        label='Save delivery information'
    )

    class Meta:
        model = Order
        fields = ['full_name', 'delivery_address', 'delivery_date', 'notes']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Full Name'
            }),
            'delivery_address': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Delivery Address',
                'rows': 3
            }),
            'delivery_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Additional notes (optional)',
                'rows': 2
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and user.address:
            self.fields['delivery_address'].initial = user.address
            self.fields['full_name'].initial = user.get_full_name() or user.username
