from django import forms
from user.models import Profile, User
from allauth.account.forms import SignupForm


class UserRegistrationForm(SignupForm):
    email = forms.EmailField(required= True)
    firstname = forms.CharField(required=True)
    lastname = forms.CharField(required=False)
    image = forms.ImageField(required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        self.fields['firstname'].widget.attrs['placeholder'] = 'firstname'
        self.fields['lastname'].widget.attrs['placeholder'] = 'lastname'
        self.fields['image'].widget.attrs['placeholder'] = 'Profile pics'


    def save(self, request):
        user = super(UserRegistrationForm, self).save(request)
        user.firstname = self.cleaned_data['firstname']
        user.lastname = self.cleaned_data['lastname']
        if 'image' in self.cleaned_data:
            user.profile.image = self.cleaned_data['image']
        user.save()
        return user
        

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', ]


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['firstname', 'lastname', ]
