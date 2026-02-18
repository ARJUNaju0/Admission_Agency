from django import forms
from .models import Inquiry

class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ['student_name', 'email', 'phone', 'message', 'course']
        widgets = {
            'student_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-secondary focus:border-transparent',
                'placeholder': 'John Doe'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-secondary',
                'placeholder': 'john@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-secondary',
                'placeholder': '+91 98765 43210'
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-secondary',
                'rows': 3,
                'placeholder': 'Any specific questions?'
            }),
            'course': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-secondary bg-white'
            })
        }

    def __init__(self, *args, **kwargs):
        # We need to filter courses based on the college context if provided
        college_id = kwargs.pop('college_id', None)
        super().__init__(*args, **kwargs)
        if college_id:
            from colleges.models import Course
            self.fields['course'].queryset = Course.objects.filter(colleges__id=college_id)

class InquiryResponseForm(forms.Form):
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-secondary focus:border-transparent',
            'placeholder': 'Email subject'
        })
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-secondary focus:border-transparent',
            'rows': 8,
            'placeholder': 'Type your response here...'
        })
    )