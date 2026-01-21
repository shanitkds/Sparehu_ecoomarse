from django.contrib.auth.forms import UserCreationForm
from .models import User
from django import forms
from django.contrib.auth import authenticate


class Registration(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "w-full rounded-3xl p-3 bg-zinc-900 text-white border border-zinc-700",
            "placeholder": "User Name"
        }))
    
    email=forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class':"w-full rounded-3xl p-3 bg-zinc-900 text-white border border-zinc-700",
            'placeholder':"Enter Email"
        }))
    
    password1=forms.CharField(
        widget=forms.PasswordInput(attrs={
             'class':"w-full rounded-3xl p-3 bg-zinc-900 text-white border border-zinc-700",
            'placeholder':"password1"
        })
    )
    
    password2=forms.CharField(
        widget=forms.PasswordInput(attrs={
             'class':"w-full rounded-3xl p-3 bg-zinc-900 text-white border border-zinc-700",
            'placeholder':"password1"
        })
    )
    
    class Meta:
        model=User
        fields=['username','email','password1','password2']
        

class Login(forms.Form):
    email=forms.EmailField(widget=forms.EmailInput(attrs={
        "class":"w-full rounded-3xl p-3 ",
        "placeholder":"Email Address"
    }))
    password=forms.CharField(widget=forms.PasswordInput(attrs={
        "class":"w-full rounded-3xl p-3 ",
        "placeholder":"Password"
    }))
    
    def clean(self):
        email=self.cleaned_data.get('email')
        password=self.cleaned_data.get('password')
        
        user=authenticate(username=email,password=password)
        if not user:
            raise forms.ValidationError("Invalid User")
        self.user=user
        return self.cleaned_data
    def get_user(self):
        return self.user
    