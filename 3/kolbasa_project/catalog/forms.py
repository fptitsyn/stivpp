from django import forms
from .models import Kolbasa, Kind

class KolbasaForm(forms.ModelForm):
    class Meta:
        model = Kolbasa
        fields = ['article', 'brand', 'kind', 'weight', 'precut', 'num_of_slices']
        widgets = {
            'article': forms.TextInput(attrs={'class': 'form-control'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'kind': forms.Select(attrs={'class': 'form-select'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'min': 50, 'max': 5000}),
            'precut': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'num_of_slices': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
        labels = {
            'article': 'Артикул',
            'brand': 'Бренд',
            'kind': 'Тип колбасы',
            'weight': 'Вес (г)',
            'precut': 'Нарезка',
            'num_of_slices': 'Количество кусочков',
        }

    def clean_article(self):
        article = self.cleaned_data.get('article')
        if Kolbasa.objects.filter(article=article).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Колбаса с таким артикулом уже существует.')
        return article