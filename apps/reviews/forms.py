from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    """Form for creating reviews"""

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': 1,
                'max': 5,
                'placeholder': 'Rating (1-5)'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Write your review here...',
                'rows': 4
            }),
        }
