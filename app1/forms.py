from django import forms
from .models import Contact,Review

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'message': forms.Textarea(attrs={'placeholder': 'Message', 'rows': 6}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('user_name', 'email', 'rating', 'title', 'body')
        widgets = {
            'rating': forms.Select(choices=[(i,i) for i in range(1,6)]),
            'body': forms.Textarea(attrs={'rows':4}),
        }
