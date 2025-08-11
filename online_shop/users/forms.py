from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django import forms
from .models import User
from django.core.exceptions import ValidationError


class UserAuthentication(UserCreationForm):
    class Meta:
        model = User

        fields = (
            "username",
            "email",
            "password1",
            "password2"
        )

        username = forms.CharField()
        email = forms.EmailField()
        password1 = forms.IntegerField()
        password2 = forms.IntegerField()

    def clean_email(self):
        email = self.cleaned_data.get('email')
        email_taken = User.objects.filter(email=email).exists()
        if email_taken:
            raise ValidationError("Email is already in use")
        return email


class EmailVerification(forms.Form):
    verification_code = forms.IntegerField()


class UserLogin(AuthenticationForm):
    class Meta:
        model = User

        fields = (
            "username",
            "password"
        )


class UserProfile(UserChangeForm):
    class Meta:
        model = User
        fields = (
            "profile_pic",
            "first_name",
            "last_name",)

    profile_pic = forms.ImageField(required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)


class EmailForPasswordReset(forms.Form):
    email = forms.EmailField()

    def clean_email(self):
        email = self.cleaned_data['email']
        associated_account = User.objects.filter(email__iexact=email).exists()
        if associated_account:
            return email


class PasswordReset(forms.Form):
    password1 = forms.CharField()
    password2 = forms.CharField()

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password1') != cleaned_data.get('password2'):
            raise ValidationError("Passwords don't match")
        return cleaned_data