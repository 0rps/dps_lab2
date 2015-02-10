from django import forms

class RegisterForm(forms.Form):
	name = forms.CharField(label='Your name', max_length=32)
	email = forms.EmailField(label='Email')
	phone = forms.CharField(label='Your phone', max_length=16)
	password = forms.CharField(label='Password', max_length=32)


class SigninForm(forms.Form):
	email = forms.EmailField(label='Your email')
	password = forms.CharField(label='Your password', max_length=32)
	redirect_uri = forms.CharField(widget=forms.HiddenInput())
	client_id = forms.CharField(widget=forms.HiddenInput())