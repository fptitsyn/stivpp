from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Kolbasa, Kind
from .forms import KolbasaForm

def product_list(request):
    """Список товаров с поиском и фильтрацией."""
    queryset = Kolbasa.objects.all().order_by('brand')

    # Поиск по бренду или названию типа
    search_query = request.GET.get('q', '')
    if search_query:
        queryset = queryset.filter(
            Q(brand__icontains=search_query) | Q(kind__name__icontains=search_query)
        )

    # Фильтр по типу колбасы (по ID типа)
    kind_filter = request.GET.get('kind', '')
    if kind_filter:
        queryset = queryset.filter(kind_id=kind_filter)

    # Фильтр по наличию нарезки
    precut_filter = request.GET.get('precut', '')
    if precut_filter == 'yes':
        queryset = queryset.filter(precut=True)
    elif precut_filter == 'no':
        queryset = queryset.filter(precut=False)

    # Получаем все типы колбас для выпадающего списка
    kinds = Kind.objects.all()

    context = {
        'title': 'Каталог колбас',
        'kolbasas': queryset,
        'search_query': search_query,
        'kinds': kinds,
        'selected_kind': kind_filter,
        'selected_precut': precut_filter,
    }
    return render(request, 'catalog/product_list.html', context)

def product_detail(request, pk):
    """Детальная страница товара."""
    kolbasa = get_object_or_404(Kolbasa, pk=pk)
    try:
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

def product_create(request):
    """Добавление нового товара."""
    if request.method == 'POST':
        form = KolbasaForm(request.POST)
        if form.is_valid():
            kolbasa = form.save()
            messages.success(request, f'Колбаса "{kolbasa.brand}" успешно добавлена!')
            return redirect('product_detail', pk=kolbasa.pk)
    else:
        form = KolbasaForm()
    return render(request, 'catalog/product_form.html', {
        'form': form,
        'title': 'Добавить колбасу',
        'submit_text': 'Добавить'
    })

def product_edit(request, pk):
    """Редактирование товара."""
    kolbasa = get_object_or_404(Kolbasa, pk=pk)
    if request.method == 'POST':
        form = KolbasaForm(request.POST, instance=kolbasa)
        if form.is_valid():
            kolbasa = form.save()
            messages.success(request, f'Колбаса "{kolbasa.brand}" обновлена!')
            return redirect('product_detail', pk=kolbasa.pk)
    else:
        form = KolbasaForm(instance=kolbasa)
    return render(request, 'catalog/product_form.html', {
        'form': form,
        'title': f'Редактировать: {kolbasa.brand}',
        'submit_text': 'Сохранить'
    })

def product_delete(request, pk):
    """Удаление товара."""
    kolbasa = get_object_or_404(Kolbasa, pk=pk)
    if request.method == 'POST':
        brand = kolbasa.brand
        kolbasa.delete()
        messages.success(request, f'Колбаса "{brand}" удалена.')
        return redirect('product_list')
    return render(request, 'catalog/product_confirm_delete.html', {
        'kolbasa': kolbasa,
        'title': f'Удалить {kolbasa.brand}?'
    })

def about(request):
    """О сервисе."""
    return render(request, 'catalog/about.html', {'title': 'О нашем сервисе'})