from django import forms
from .models.manga import Manga, VolumeManga, Genre
from django.contrib.auth.models import User
from .models import Profile
from django.forms import modelformset_factory


class MangaForm(forms.ModelForm):
    class Meta:
        model = Manga
        fields = ['image','title', 'author', 'description','genre']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})
# class MangaForm(forms.ModelForm):
#     genre = forms.ModelMultipleChoiceField(
#         queryset=Genre.objects.all(),
#         widget=forms.CheckboxSelectMultiple(attrs={'class': 'custom-checkbox'})
#     )

#     class Meta:
#         model = Manga
#         fields = ['image', 'title', 'author', 'description', 'genre']
#         widgets = {
#             'description': forms.Textarea(attrs={'rows': 4}),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for field in self.fields.values():
#             field.widget.attrs.update({"class": "form-control"})

        
VolumeFormSet = modelformset_factory(
    VolumeManga,
    fields=['volume', 'price', 'stock'],
    extra=0,
    can_delete= True,
)
    
        
class UserRegistrationForm(forms.ModelForm):
    ROLE_CHOICES=[
        ('Seller', 'Seller'),
        ('Customer', 'Customer'),
    ]
    
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)
    address = forms.CharField(widget=forms.Textarea)
    phone_number = forms.CharField(max_length=20)
    image = forms.ImageField(required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
            
            Profile.objects.create(
                user=user,
                address=self.cleaned_data['address'],
                phone_number=self.cleaned_data['phone_number'],
                picture=self.cleaned_data.get('image')
            )
        return user
