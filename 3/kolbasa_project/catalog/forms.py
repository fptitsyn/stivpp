from django import forms
from .models import Kolbasa, Cart, CartItem


class KolbasaForm(forms.ModelForm):
    class Meta:
        model = Kolbasa
        fields = [
            'article', 'brand', 'kind', 'weight', 'precut', 'num_of_slices',
            'price_unit', 'price_small_opt', 'price_large_opt',
            'qty_small_opt', 'qty_large_opt',
        ]
        widgets = {
            'article': forms.TextInput(attrs={'class': 'form-control'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'kind': forms.Select(attrs={'class': 'form-select'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'min': 50, 'max': 5000}),
            'precut': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'num_of_slices': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'price_unit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'price_small_opt': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'price_large_opt': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'qty_small_opt': forms.NumberInput(attrs={'class': 'form-control'}),
            'qty_large_opt': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'article': 'Артикул',
            'brand': 'Бренд',
            'kind': 'Тип колбасы',
            'weight': 'Вес (г)',
            'precut': 'Нарезка',
            'num_of_slices': 'Количество кусочков',
            'price_unit': 'Цена за единицу',
            'price_small_opt': 'Цена мелкий опт',
            'price_large_opt': 'Цена крупный опт',
            'qty_small_opt': 'Кол-во для мелкого опта',
            'qty_large_opt': 'Кол-во для крупного опта',
        }


class CartItemForm(forms.ModelForm):
    class Meta:
        model = CartItem
        fields = ['quantity']
        widgets = {'quantity': forms.NumberInput(attrs={'min': 1, 'class': 'form-control'})}


class CartDiscountForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = ['discount_percent']
        widgets = {'discount_percent': forms.NumberInput(attrs={'min': 0, 'max': 100, 'class': 'form-control'})}
