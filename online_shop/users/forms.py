from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django import forms
from django.contrib import auth
from .models import User



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
        email = forms.CharField()
        password1 = forms.CharField()
        password2 = forms.CharField()


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
            "last_name",
            "username",
            "email",)

        profile_pic = forms.ImageField(required=False)
        first_name = forms.CharField(required=False)
        last_name = forms.CharField(required=False)
        username = forms.CharField()
        email = forms.CharField()