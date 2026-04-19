from django.shortcuts import render, get_object_or_404
from .models import Kolbasa

def product_list(request):
    """
    Главная страница — список всех колбас из базы данных.
    """
    kolbasas = Kolbasa.objects.all().order_by('brand')
    context = {
        'title': 'Каталог колбас',
        'kolbasas': kolbasas,
    }
    return render(request, 'catalog/product_list.html', context)

def product_detail(request, pk):
    """
    Детальная страница конкретной колбасы по её id (pk).
    """
    kolbasa = get_object_or_404(Kolbasa, pk=pk)
    try:
        # Вычисляем вес кусочка (может вызвать ValueError, если не нарезка)
        weight_per_slice = kolbasa.weight_per_slice if kolbasa.precut else None
    except ValueError as e:
        weight_per_slice = None
        error_msg = str(e)
    else:
        error_msg = None

    context = {
        'title': f'Колбаса {kolbasa.brand}',
        'kolbasa': kolbasa,
        'weight_per_slice': weight_per_slice,
        'error_msg': error_msg,
    }
    return render(request, 'catalog/product_detail.html', context)

def about(request):
    """
    Страница с информацией о сервисе.
    """
    context = {
        'title': 'О нашем сервисе',
        'description': 'Мы продаём лучшие колбасы с доставкой на дом. Качество подтверждено сертификатами.',
    }
    return render(request, 'catalog/about.html', context)