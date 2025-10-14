from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Userprofile

class CustomSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    mobile_number = forms.CharField(max_length=20, required=True)
    province = forms.ChoiceField(choices=Userprofile.PROVINCES, required=True)
    city = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2',
            'mobile_number',
            'province',
            'city'
        ]

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Userprofile.objects.create(
                user=user,
                mobile_number=self.cleaned_data['mobile_number'],
                province=self.cleaned_data['province'],
                city=self.cleaned_data['city']
            )
        return user



class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Userprofile
        fields = ['avatar', 'bio', 'province', 'city', 'mobile_number', ]  # include the fields you want editable
