from django import forms
from django.forms.models import inlineformset_factory
from .models.manga import Manga, Genre

class MangaForm(forms.ModelForm):
    class Meta:
        model = Manga
        fields = ['image', 'title', 'author', 'genre', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'genre': forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['genre'].queryset = Genre.objects.all()

