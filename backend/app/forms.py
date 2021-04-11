from django import forms


class UserAuthForm(forms.Form):
    username = forms.CharField(max_length=50)
    password = forms.CharField(max_length=100, widget=forms.PasswordInput)


class UserRegisterForm(forms.Form):
    email = forms.CharField(max_length=150)
    username = forms.CharField(max_length=50)
    password = forms.CharField(max_length=100, widget=forms.PasswordInput)
    password_repeat = forms.CharField(max_length=100, widget=forms.PasswordInput)
