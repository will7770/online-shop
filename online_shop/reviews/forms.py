from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    RATING_CHOICES = [
        (5, '★★★★★'),
        (4, '★★★★☆'),
        (3, '★★★☆☆'),
        (2, '★★☆☆☆'),
        (1, '★☆☆☆☆'),
    ]
    
    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'rating-radio'}),
        required=True
    )
    
    class Meta:
        model = Review
        fields = ['rating', 'title', 'text']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Summarize your experience'
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share details of your experience'
            }),
        }
        labels = {
            'text': 'Your Review'
        }
    